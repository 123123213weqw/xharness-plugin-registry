#!/usr/bin/env python3
"""Build opt-in reviewed releases deterministically; versions are immutable."""
import hashlib, io, json, re, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://raw.githubusercontent.com/123123213weqw/xharness-plugin-registry/main/'
MIRROR = 'https://gitee.com/api/v5/repos/wangyue2006/xharness-plugin-registry/contents/'
EXCLUDED = {'registry.json'}  # catalogue-only; Github 0.2.0 archive stays unchanged

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
        relative = f'packages/{name}/{version}/plugin.zip'
        target = root / relative; target.parent.mkdir(parents=True, exist_ok=True)
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
