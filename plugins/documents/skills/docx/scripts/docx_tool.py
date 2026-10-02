#!/usr/bin/env python3
"""SPDX-License-Identifier: MIT. Independently authored document operations.

Bounded create/read/replace and adjacent same-format run normalization. No vendor imports, network, shell or embedded
content execution. Rendering is a separate official-tool acceptance gate.
"""
import argparse
import hashlib
import json
import os
import posixpath
import stat
import sys
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
MAX_ARCHIVE_BYTES = 10 * 1024 * 1024
MAX_JSON_BYTES = 256 * 1024
NS = {'w': W}


class InputError(ValueError):
    pass


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def xml_root(payload):
    if b'<!DOCTYPE' in payload or b'<!ENTITY' in payload:
        raise InputError('DTD and entities are not supported')
    try:
        return etree.fromstring(payload, etree.XMLParser(resolve_entities=False, no_network=True))
    except etree.XMLSyntaxError as exc:
        raise InputError('malformed XML part') from exc


def read_package(path):
    path = Path(path)
    if not path.exists() or not path.is_file():
        raise InputError('input file does not exist')
    if not path.stat().st_size:
        raise InputError('empty document bytes')
    if path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise InputError('archive exceeds byte limit')
    try:
        with zipfile.ZipFile(path) as zf:
            infos = zf.infolist()
            names = [i.filename for i in infos]
            if len(infos) > 512 or len(set(names)) != len(names):
                raise InputError('too many or duplicate archive members')
            if sum(i.file_size for i in infos) > MAX_ARCHIVE_BYTES:
                raise InputError('expanded archive exceeds byte limit')
            parts = {}
            for info in infos:
                name = info.filename
                if name.startswith('/') or '\\' in name or '..' in name.split('/') or stat.S_ISLNK(info.external_attr >> 16):
                    raise InputError('unsafe ZIP path or symlink')
                if name.startswith('_xmlsignatures/') or name.endswith('vbaProject.bin'):
                    raise InputError('signed or macro-bearing documents are outside this tool scope')
                payload = zf.read(info)
                if name.endswith(('.xml', '.rels')):
                    xml_root(payload)
                parts[name] = payload
    except (zipfile.BadZipFile, RuntimeError) as exc:
        raise InputError('corrupt ZIP document') from exc
    if not {'[Content_Types].xml', '_rels/.rels', 'word/document.xml', 'word/styles.xml'} <= set(parts):
        raise InputError('missing required DOCX parts')
    external = []
    for name, payload in parts.items():
        if not name.endswith('.rels'):
            continue
        base = '' if name == '_rels/.rels' else posixpath.dirname(posixpath.dirname(name))
        for rel in xml_root(payload):
            target = rel.get('Target', '')
            if rel.get('TargetMode') == 'External':
                external.append({'relationship_part': name, 'target': target, 'executed': False})
                continue
            target = (target.lstrip('/') if target.startswith('/') else
                      posixpath.normpath(posixpath.join(base, target)))
            if target not in parts:
                raise InputError('unresolved internal relationship')
    return parts, external


def load_plan(path):
    raw = Path(path).read_bytes()
    if not raw:
        raise InputError('empty JSON input')
    if len(raw) > MAX_JSON_BYTES:
        raise InputError('JSON input exceeds byte limit')
    try:
        obj = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise InputError('invalid JSON input') from exc
    if not isinstance(obj, dict) or not {'title', 'introduction', 'blocks'} <= set(obj) or set(obj) - {'title', 'introduction', 'blocks', 'page_numbers', 'author', 'footer_label'}:
        raise InputError('invalid plan keys')
    bounded_text(obj['title'], 'title', 120)
    bounded_text(obj['introduction'], 'introduction', 2000)
    if 'author' in obj:
        bounded_text(obj['author'], 'author', 120)
    if 'footer_label' in obj:
        bounded_text(obj['footer_label'], 'footer_label', 120)
    if 'page_numbers' in obj and not isinstance(obj['page_numbers'], bool):
        raise InputError('page_numbers must be boolean')
    if not isinstance(obj['blocks'], list) or not 1 <= len(obj['blocks']) <= 100:
        raise InputError('blocks outside supported range')
    for block in obj['blocks']:
        if not isinstance(block, dict):
            raise InputError('block must be object')
        kind = block.get('type')
        if kind == 'paragraph':
            if set(block) != {'type', 'text'}:
                raise InputError('invalid paragraph keys')
            bounded_text(block['text'], kind, 2000)
        elif kind == 'heading':
            if set(block) != {'type', 'text', 'level'} or type(block['level']) is not int or not 1 <= block['level'] <= 3:
                raise InputError('invalid heading')
            bounded_text(block['text'], kind, 120)
        elif kind == 'list':
            if set(block) != {'type', 'items', 'ordered'} or not isinstance(block['ordered'], bool):
                raise InputError('invalid list keys')
            if not isinstance(block['items'], list) or not 1 <= len(block['items']) <= 25:
                raise InputError('list items outside range')
            for item in block['items']:
                bounded_text(item, 'list item', 500)
        elif kind == 'table':
            if set(block) != {'type', 'headers', 'rows', 'widths_inches'}:
                raise InputError('invalid table keys')
            headers, rows, widths = block['headers'], block['rows'], block['widths_inches']
            if not isinstance(headers, list) or not 1 <= len(headers) <= 8 or not isinstance(rows, list) or not 1 <= len(rows) <= 25:
                raise InputError('table shape outside range')
            if not isinstance(widths, list) or len(widths) != len(headers) or any(type(x) not in (int, float) or not 0.5 <= x <= 6.5 for x in widths) or abs(sum(widths) - 6.5) > 0.001:
                raise InputError('table widths must sum to content width 6.5 inches')
            for row in [headers] + rows:
                if not isinstance(row, list) or len(row) != len(headers):
                    raise InputError('table row width mismatch')
                for value in row:
                    bounded_text(value, 'table cell', 500)
        elif kind == 'page_break':
            if set(block) != {'type'}:
                raise InputError('invalid page break keys')
        else:
            raise InputError('unsupported block type')
    return obj


def bounded_text(value, label, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any((ord(c) < 32 and c not in '\t\n\r') or 0xD800 <= ord(c) <= 0xDFFF or ord(c) in (0xFFFE, 0xFFFF) for c in value):
        raise InputError('invalid text ' + label)


def reserve_output(output, source=None):
    path = Path(output)
    if path.exists() or (source and path.resolve() == Path(source).resolve()):
        raise InputError('refusing existing output or in-place mutation')
    if not path.parent.is_dir():
        raise InputError('output parent does not exist')
    return path


def publish_atomic(output, serializer, validate):
    """Exclusively link a validated sibling file; never replace an existing name."""
    fd, temporary_name = tempfile.mkstemp(prefix='.docx-tool-', suffix='.tmp', dir=output.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        serializer(temporary)
        validate(temporary)
        with temporary.open('rb') as stream:
            os.fsync(stream.fileno())
        try:
            os.link(temporary, output, follow_symlinks=False)
        except FileExistsError as exc:
            raise InputError('exclusive publish refused existing output') from exc
    finally:
        temporary.unlink(missing_ok=True)


def create_document(plan_path, output):
    plan = load_plan(plan_path)
    output = reserve_output(output)
    document = Document()
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(1)
    document.core_properties.author = plan.get('author', 'Independent document tool')
    document.core_properties.title = plan['title']
    for name in ('Normal', 'Title', 'Heading 1', 'Heading 2', 'Heading 3', 'List Number', 'List Bullet', 'Footer'):
        style = document.styles[name]
        style.font.name = 'Arial'
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.size = Pt(11 if name not in ('Title', 'Heading 1', 'Heading 2', 'Heading 3') else {'Title': 22, 'Heading 1': 14, 'Heading 2': 12, 'Heading 3': 11}[name])
        style.paragraph_format.space_after = Pt(6)
        if name == 'Title':
            for border in list(style.element.xpath('./w:pPr/w:pBdr')):
                border.getparent().remove(border)
    document.add_paragraph(plan['title'], 'Title')
    document.add_paragraph(plan['introduction'])
    for block in plan['blocks']:
        kind = block['type']
        if kind == 'paragraph':
            document.add_paragraph(block['text'])
        elif kind == 'heading':
            document.add_heading(block['text'], block['level'])
        elif kind == 'list':
            for item in block['items']:
                document.add_paragraph(item, 'List Number' if block['ordered'] else 'List Bullet')
        elif kind == 'page_break':
            document.add_page_break()
        elif kind == 'table':
            table = document.add_table(rows=1, cols=len(block['headers']))
            table.style = 'Table Grid'
            table.autofit = False
            table._tbl.tblPr.find(qn('w:tblW')).set(qn('w:type'), 'dxa')
            table._tbl.tblPr.find(qn('w:tblW')).set(qn('w:w'), '9360')
            for column, width in zip(table.columns, block['widths_inches']):
                column.width = Inches(width)
            for index, values in enumerate([block['headers']] + block['rows']):
                row = table.rows[0] if index == 0 else table.add_row()
                rp = row._tr.get_or_add_trPr()
                rp.append(OxmlElement('w:cantSplit'))
                if index == 0:
                    rp.append(OxmlElement('w:tblHeader'))
                for cell, text, width in zip(row.cells, values, block['widths_inches']):
                    cell.width = Inches(width)
                    cell.text = text
                    cp = cell._tc.get_or_add_tcPr()
                    margins = OxmlElement('w:tcMar')
                    for side in ('top', 'left', 'bottom', 'right'):
                        margin = OxmlElement('w:' + side)
                        margin.set(qn('w:w'), '120')
                        margin.set(qn('w:type'), 'dxa')
                        margins.append(margin)
                    cp.append(margins)
                    if index == 0:
                        shading = OxmlElement('w:shd')
                        shading.set(qn('w:val'), 'clear')
                        shading.set(qn('w:fill'), 'E7E6E6')
                        cp.append(shading)
                        for p in cell.paragraphs:
                            for run in p.runs:
                                run.bold = True
    if plan.get('page_numbers', True):
        p = section.footer.paragraphs[0]
        p.style = document.styles['Footer']
        p.add_run((plan['footer_label'] + '   ' if 'footer_label' in plan else '') + 'Page ')
        field = OxmlElement('w:fldSimple')
        field.set(qn('w:instr'), 'PAGE')
        p._p.append(field)
    publish_atomic(output, document.save, read_package)
    return inspect_document(output)


def inspect_document(path):
    parts, external = read_package(path)
    root = xml_root(parts['word/document.xml'])
    body = root.find('w:body', NS)
    paragraphs = []
    tables = []
    for child in body:
        if child.tag == '{' + W + '}p':
            paragraphs.append(''.join(child.xpath('.//w:t/text()', namespaces=NS)))
        elif child.tag == '{' + W + '}tbl':
            tables.append([[''.join(cell.xpath('.//w:t/text()', namespaces=NS)) for cell in row.findall('w:tc', NS)] for row in child.findall('w:tr', NS)])
    revisions = len(root.xpath('.//w:ins | .//w:del', namespaces=NS))
    return {'path': str(Path(path).resolve()), 'sha256': digest(path), 'bytes': Path(path).stat().st_size,
            'paragraphs': paragraphs, 'tables': tables, 'parts': sorted(parts),
            'external_relationships': external, 'tracked_revision_elements': revisions,
            'limitations': ['This is ordinary body/table text, not accepted/original tracked-change views.',
                            'ZIP/XML/relationship checks are not full OOXML XSD validation.',
                            'Rendering and visual QA are separate.']}


def replace_complete_run(source, output, old, new):
    bounded_text(old, 'old text', 2000)
    bounded_text(new, 'new text', 2000)
    output = reserve_output(output, source)
    parts, _ = read_package(source)
    root = xml_root(parts['word/document.xml'])
    if root.xpath('.//w:ins | .//w:del', namespaces=NS):
        raise InputError('tracked-change editing is outside tool scope')
    targets = [t for t in root.xpath('.//w:t', namespaces=NS) if t.text == old]
    if len(targets) != 1:
        raise InputError('replacement requires exactly one complete text run; split runs unsupported')
    targets[0].text = new
    parts['word/document.xml'] = etree.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)
    def serialize(temporary):
        with zipfile.ZipFile(source) as source_zip, zipfile.ZipFile(temporary, 'w') as dest:
            for info in source_zip.infolist():
                dest.writestr(info, parts[info.filename])
    publish_atomic(output, serialize, read_package)
    return inspect_document(output)


def merge_adjacent_runs(root):
    """Merge only consecutive direct pure text runs with identical rPr/attrs.

    No field, hyperlink, bookmark, comment, drawing or revision is traversed as
    a bridge. Equivalent-but-differently-spelled properties are not merged.
    This normalizes body/table paragraph runs, not the other document parts.
    """
    def signature(run):
        if run.tag != '{' + W + '}r' or (run.tail and run.tail.strip()):
            return None
        children = list(run)
        properties = children.pop(0) if children and children[0].tag == '{' + W + '}rPr' else None
        if not children or any(c.tag != '{' + W + '}t' or len(c) or set(c.attrib) - {'{http://www.w3.org/XML/1998/namespace}space'} or c.get('{http://www.w3.org/XML/1998/namespace}space', 'default') not in ('default', 'preserve') or (c.tail and c.tail.strip()) for c in children):
            return None
        if run.text and run.text.strip():
            return None
        if properties is not None and properties.tail and properties.tail.strip():
            return None
        prop_bytes = etree.tostring(properties, method='c14n', exclusive=True, with_comments=True, with_tail=False) if properties is not None else None
        return tuple(sorted(run.attrib.items())), prop_bytes

    if root.tag != '{' + W + '}document' or root.find('w:body', NS) is None:
        raise InputError('ordinary document body required')
    if root.xpath('.//w:ins | .//w:del | .//w:moveFrom | .//w:moveTo | .//w:rPrChange', namespaces=NS):
        raise InputError('tracked-change run normalization is outside tool scope')
    before_text = tuple(root.xpath('.//w:t/text()', namespaces=NS))
    groups = []
    for paragraph_index, paragraph in enumerate(root.xpath('./w:body//w:p', namespaces=NS)):
        # Preserve textboxes/content controls/other nested wrappers untouched.
        containers = []
        for ancestor in paragraph.iterancestors():
            if ancestor.tag == '{' + W + '}body':
                break
            containers.append(ancestor.tag)
        if any(tag not in {'{' + W + '}tc', '{' + W + '}tr', '{' + W + '}tbl'} for tag in containers):
            continue
        children = list(paragraph)
        index = 0
        while index < len(children):
            first = children[index]
            key = signature(first)
            if key is None:
                index += 1
                continue
            end = index + 1
            while end < len(children) and signature(children[end]) == key:
                end += 1
            if end - index > 1:
                group = children[index:end]
                texts = [t for r in group for t in r.findall('w:t', NS)]
                combined = ''.join(t.text or '' for t in texts)
                texts[0].text = combined
                texts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                for t in list(first.findall('w:t', NS))[1:]:
                    first.remove(t)
                for run in group[1:]:
                    paragraph.remove(run)
                groups.append({'paragraph_index': paragraph_index, 'original_runs': len(group),
                               'removed_runs': len(group) - 1, 'text': combined})
            index = end
    if ''.join(before_text) != ''.join(root.xpath('.//w:t/text()', namespaces=NS)):
        raise InputError('normalization changed literal document text')
    return groups


def normalize_runs(source, output):
    output = reserve_output(output, source)
    source_sha = digest(source)
    parts, _ = read_package(source)
    original = dict(parts)
    root = xml_root(parts['word/document.xml'])
    groups = merge_adjacent_runs(root)
    if groups:
        parts['word/document.xml'] = etree.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)

    def serialize(temporary):
        with zipfile.ZipFile(source) as source_zip, zipfile.ZipFile(temporary, 'w') as dest:
            for info in source_zip.infolist():
                dest.writestr(info, parts[info.filename])

    def validate(temporary):
        actual, _ = read_package(temporary)
        if actual != parts or digest(source) != source_sha:
            raise InputError('saved package/source preservation mismatch before publication')

    publish_atomic(output, serialize, validate)
    return {**inspect_document(output), 'source_sha256': source_sha,
            'merged_groups': groups, 'removed_runs': sum(g['removed_runs'] for g in groups),
            'changed_parts': ['word/document.xml'] if groups else [],
            'other_uncompressed_parts_preserved': all(original[n] == parts[n] for n in original if n != 'word/document.xml'),
            'scope': 'body/table direct adjacent pure text runs, identical canonical rPr and run attributes only; no header/footer/field/revision/hyperlink normalization'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('operation', choices=['create', 'inspect', 'replace', 'merge-runs'])
    ap.add_argument('--input', required=True)
    ap.add_argument('--output')
    ap.add_argument('--old')
    ap.add_argument('--new')
    args = ap.parse_args()
    try:
        if args.operation == 'inspect':
            result = inspect_document(args.input)
        elif not args.output:
            raise InputError('output required for authoring')
        elif args.operation == 'create':
            result = create_document(args.input, args.output)
        elif args.operation == 'merge-runs':
            if args.old is not None or args.new is not None:
                raise InputError('merge-runs does not accept replacement text')
            result = normalize_runs(args.input, args.output)
        elif args.old is None or args.new is None:
            raise InputError('old and new text required for replacement')
        else:
            result = replace_complete_run(args.input, args.output, args.old, args.new)
        print(json.dumps({'ok': True, 'operation': args.operation, 'pid': os.getpid(), 'result': result}, ensure_ascii=False))
        return 0
    except (InputError, OSError) as exc:
        print(json.dumps({'ok': False, 'operation': args.operation, 'pid': os.getpid(), 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
