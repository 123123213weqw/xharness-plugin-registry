#!/usr/bin/env python3
"""Build opt-in reviewed releases deterministically; versions are immutable."""
import hashlib, io, json, re, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://raw.githubusercontent.com/123123213weqw/xharness-plugin-registry/main/'
MIRROR = 'https://gitee.com/api/v5/repos/wangyue2006/xharness-plugin-registry/contents/'
EXCLUDED = {'registry.json'}  # listing-only metadata is never package payload

def verified_prebuilt(plugin, target, name, version):
    """Reviewed compiled editor payload, not a source-reproducible WASM claim.

    There is one immutable archive, not a second 89 MB WASM in source control.
    The Host independently pins this ZIP and each exposed asset at installation.
    """
    record = json.loads((plugin/'prebuilt.json').read_text())
    if record.get('format') != 1 or not target.is_file(): raise ValueError('missing pinned prebuilt archive')
    content = target.read_bytes()
    if len(content) != record['bytes'] or hashlib.sha256(content).hexdigest() != record['sha256']:
        raise ValueError('prebuilt archive changed; bump version and review the new binding')
    if len(content) > 64*1024*1024: raise ValueError('prebuilt archive too large')
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or len(names) > 128: raise ValueError('invalid prebuilt file list')
        if sum(i.file_size for i in archive.infolist()) != record['unpackedBytes'] or record['unpackedBytes'] > 128*1024*1024:
            raise ValueError('prebuilt unpacked budget exceeded')
        for entry in archive.infolist():
            path = Path(entry.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in entry.filename or not entry.filename.startswith(name+'/') or entry.is_dir():
                raise ValueError('unsafe prebuilt path')
            if (entry.external_attr >> 16) & 0o170000 != 0o100000: raise ValueError('non-regular prebuilt file')
            if any(part in {'.git','node_modules','target','__pycache__'} or part.startswith('.env') for part in path.parts):
                raise ValueError('private prebuilt path')
        for path in ['.claude-plugin/plugin.json','RELEASE.md','LICENSE']:
            if archive.read(name+'/'+path) != (plugin/path).read_bytes(): raise ValueError('prebuilt review metadata mismatch')
        manifest = json.loads(archive.read(name+'/.claude-plugin/plugin.json'))
        if (manifest['name'],manifest['version']) != (name,version): raise ValueError('prebuilt identity mismatch')
        panel = json.loads(archive.read(name+'/.xharness-ui.json'))
        if panel['version'] != 1 or panel['resourceUri'] != 'ui://'+name+'/panel.html': raise ValueError('invalid UI binding')
        wasm = []
        for path, asset in panel['assets'].items():
            if '..' in Path(path).parts: raise ValueError('unsafe asset path')
            data = archive.read(name+'/'+path)
            if len(data) != asset['bytes'] or hashlib.sha256(data).hexdigest() != asset['sha256']:
                raise ValueError('invalid asset binding')
            if path.endswith('.wasm'): wasm.append(asset['sha256'])
        if wasm != [record['wasmSha256']]: raise ValueError('engine binary changed')
    return content


def build(root=ROOT):
    root = Path(root); rows = []
    for plugin in sorted((root / 'plugins').iterdir()):
        if not plugin.is_dir() or plugin.is_symlink(): raise ValueError('plugin directory required')
        meta = json.loads((plugin / '.claude-plugin/plugin.json').read_text())
        name, version = meta['name'], meta['version']
        if plugin.name != name or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', name):
            raise ValueError('manifest/directory ID mismatch')
        if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?', version): raise ValueError('invalid version')
        listing = json.loads((plugin/'registry.json').read_text())
        relative = f'packages/{name}/{version}/plugin.zip'
        target = root / relative; target.parent.mkdir(parents=True, exist_ok=True)
        if (plugin/'prebuilt.json').exists():
            content = verified_prebuilt(plugin, target, name, version)
            digest = hashlib.sha256(content).hexdigest()
        else:
            data = io.BytesIO()
            with zipfile.ZipFile(data, 'w', compression=zipfile.ZIP_STORED) as archive:
                for path in sorted(plugin.rglob('*')):
                    if path.is_symlink(): raise ValueError('symlinks are not package sources')
                    relative_path = path.relative_to(plugin)
                    if {'__pycache__', 'node_modules', 'target', '.git'}.intersection(relative_path.parts): continue
                    if any(part.startswith('.env') for part in relative_path.parts): raise ValueError('environment files are not package sources')
                    if not path.is_file() or relative_path.as_posix() in EXCLUDED or path.suffix == '.pyc': continue
                    info = zipfile.ZipInfo(str(Path(name) / path.relative_to(plugin)), date_time=(2026, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_STORED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, path.read_bytes())
            content = data.getvalue(); digest = hashlib.sha256(content).hexdigest()
            if target.exists() and target.read_bytes() != content:
                raise ValueError(f'{relative} already exists with different bytes; bump version')
            if not target.exists(): target.write_bytes(content)
        rows.append({'name': name, 'version': version, **listing,
            'source': {'source': 'url', 'type': 'zip', 'url': BASE+relative,
                'mirrors': [MIRROR+relative], 'sha256': digest}})
    temporary = root/'catalog.json.tmp'
    temporary.write_text(json.dumps({'plugins': rows}, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(root/'catalog.json')

if __name__ == '__main__': build()
