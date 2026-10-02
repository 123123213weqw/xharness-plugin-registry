#!/usr/bin/env python3
"""SPDX-License-Identifier: MIT. Independent bounded PDF operations.

No vendor scripts, subprocesses, network or executable input content.
"""
import argparse
import hashlib
import html
import json
import os
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError, EmptyFileError
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle


class InputError(ValueError):
    pass


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(value, maximum=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or any(ord(c) > 255 or (ord(c) < 32 and c not in '\n\t') for c in value):
        raise InputError('text must be bounded supported Latin text')
    return value


def reserve_output(output, inputs=()):
    p = Path(output)
    if p.exists() or any(p.resolve() == Path(i).resolve() for i in inputs):
        raise InputError('existing output and in-place edits are forbidden')
    if not p.parent.is_dir():
        raise InputError('output parent does not exist')
    return p


def publish_atomic(output, serializer, validate):
    """No replace fallback: a hard link exclusively publishes a complete sibling file."""
    fd, tmp_name = tempfile.mkstemp(prefix='.pdf-tool-', suffix='.tmp', dir=output.parent)
    os.close(fd)
    temporary = Path(tmp_name)
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


def reader(path):
    p = Path(path)
    if not p.is_file():
        raise InputError('input file does not exist')
    if not p.stat().st_size:
        raise InputError('empty PDF bytes')
    if p.stat().st_size > 10 * 1024 * 1024:
        raise InputError('PDF byte limit exceeded')
    try:
        r = PdfReader(p, strict=True)
        if r.is_encrypted:
            raise InputError('encrypted PDF needs separately reviewed password workflow')
        if not 1 <= len(r.pages) <= 50:
            raise InputError('page count outside supported range')
        return r
    except (PdfReadError, EmptyFileError, ValueError) as exc:
        if isinstance(exc, InputError):
            raise
        raise InputError('corrupt or unsupported PDF') from exc


def inspect(path):
    r = reader(path)
    fields = r.get_fields() or {}
    return {'path': str(Path(path).resolve()), 'bytes': Path(path).stat().st_size, 'sha256': sha(path),
            'page_count': len(r.pages), 'pages': [{'text': p.extract_text() or '', 'rotation': p.rotation,
                                                   'media_box': [float(x) for x in p.mediabox]} for p in r.pages],
            'metadata': {str(k): str(v) for k, v in (r.metadata or {}).items()},
            'fields': {str(k): {'type': str(v.get('/FT', '')), 'value': str(v.get('/V', ''))} for k, v in fields.items()},
            'limitations': ['Not OCR, table extraction, full form/widget/appearance validation or visual QA.']}


def create(plan_path, output):
    raw = Path(plan_path).read_bytes()
    if not raw:
        raise InputError('empty JSON input')
    if len(raw) > 256 * 1024:
        raise InputError('JSON byte limit exceeded')
    try:
        plan = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise InputError('invalid JSON input') from exc
    if not isinstance(plan, dict) or set(plan) != {'title', 'author', 'pages'}:
        raise InputError('invalid plan keys')
    text(plan['title'], 120); text(plan['author'], 120)
    if not isinstance(plan['pages'], list) or not 1 <= len(plan['pages']) <= 10:
        raise InputError('logical pages outside supported range')
    for page in plan['pages']:
        if not isinstance(page, dict) or set(page) - {'heading', 'paragraphs', 'table'} or not {'heading', 'paragraphs'} <= set(page):
            raise InputError('invalid page keys')
        text(page['heading'], 120)
        if not isinstance(page['paragraphs'], list) or not 1 <= len(page['paragraphs']) <= 10:
            raise InputError('paragraph count outside range')
        for p in page['paragraphs']:
            text(p, 1000)
        if 'table' in page:
            t = page['table']
            if not isinstance(t, dict) or set(t) != {'headers', 'rows', 'widths_points'}:
                raise InputError('invalid table keys')
            if not isinstance(t['headers'], list) or not 1 <= len(t['headers']) <= 6 or not isinstance(t['rows'], list) or not 1 <= len(t['rows']) <= 15:
                raise InputError('table shape outside range')
            widths = t['widths_points']
            if not isinstance(widths, list) or len(widths) != len(t['headers']) or any(type(x) not in (int, float) or not 40 <= x <= 468 for x in widths) or abs(sum(widths) - 468) > .001:
                raise InputError('table widths must sum to 468 points')
            for row in [t['headers']] + t['rows']:
                if not isinstance(row, list) or len(row) != len(t['headers']):
                    raise InputError('table row width mismatch')
                for value in row:
                    text(value, 300)
    output = reserve_output(output)
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=11, leading=15, spaceAfter=8)
    heading_style = ParagraphStyle('Heading', parent=body_style, fontName='Helvetica-Bold', fontSize=16, leading=20, spaceAfter=14)
    cell_style = ParagraphStyle('Cell', parent=body_style, fontSize=10, leading=13, spaceAfter=0)
    story = []
    for index, page in enumerate(plan['pages']):
        if index:
            story.append(PageBreak())
        story.append(Paragraph(html.escape(page['heading']), heading_style))
        for p in page['paragraphs']:
            story.append(Paragraph(html.escape(p).replace('\n', '<br/>'), body_style))
        if 'table' in page:
            t = page['table']
            table = Table([[Paragraph(html.escape(c), cell_style) for c in row] for row in [t['headers']] + t['rows']], colWidths=t['widths_points'], repeatRows=1)
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
                                       ('GRID', (0, 0), (-1, -1), .5, colors.HexColor('#888888')),
                                       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                                       ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
            story.extend([Spacer(1, 8), table])
    def footer(canvas, doc):
        canvas.saveState(); canvas.setFont('Helvetica', 9)
        canvas.drawString(72, 40, 'Page ' + str(doc.page)); canvas.restoreState()
    def serialize(temporary):
        SimpleDocTemplate(str(temporary), pagesize=letter, leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72,
                          title=plan['title'], author=plan['author']).build(story, onFirstPage=footer, onLaterPages=footer)
    def validate(temporary):
        if len(reader(temporary).pages) != len(plan['pages']):
            raise InputError('content overflowed requested pages; reduce input before authoring')
    publish_atomic(output, serialize, validate)
    return inspect(output)


def write_pages(readers, selections, output, inputs):
    output = reserve_output(output, inputs)
    writer = PdfWriter()
    for r, pages in zip(readers, selections):
        for p in pages:
            if type(p) is not int or not 1 <= p <= len(r.pages):
                raise InputError('page selection outside actual page count')
            writer.add_page(r.pages[p - 1])
    if not 1 <= len(writer.pages) <= 50:
        raise InputError('result page count outside range')
    publish_atomic(output, writer.write, reader)
    return inspect(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['create', 'inspect', 'merge', 'select', 'rotate'])
    parser.add_argument('--input', required=True, nargs='+')
    parser.add_argument('--output')
    parser.add_argument('--pages', type=int, nargs='+')
    parser.add_argument('--angle', type=int)
    args = parser.parse_args()
    try:
        if args.operation != 'merge' and len(args.input) != 1:
            raise InputError('exactly one input required for operation')
        if args.operation == 'inspect':
            result = inspect(args.input[0])
        elif not args.output:
            raise InputError('output is required')
        elif args.operation == 'create':
            result = create(args.input[0], args.output)
        elif args.operation == 'merge':
            readers = [reader(p) for p in args.input]
            result = write_pages(readers, [list(range(1, len(r.pages) + 1)) for r in readers], args.output, args.input)
        elif args.operation == 'select':
            if not args.pages:
                raise InputError('pages are required')
            result = write_pages([reader(args.input[0])], [args.pages], args.output, args.input)
        else:
            if args.angle not in (90, 180, 270):
                raise InputError('rotation must be 90 180 or 270')
            r = reader(args.input[0])
            output = reserve_output(args.output, args.input)
            w = PdfWriter()
            for p in r.pages:
                w.add_page(p).rotate(args.angle)
            publish_atomic(output, w.write, reader)
            result = inspect(output)
        print(json.dumps({'ok': True, 'operation': args.operation, 'pid': os.getpid(), 'result': result}))
        return 0
    except (InputError, OSError, PdfReadError) as exc:
        print(json.dumps({'ok': False, 'operation': args.operation, 'pid': os.getpid(), 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
