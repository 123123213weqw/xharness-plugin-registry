#!/usr/bin/env python3
"""Build reviewed plugin sources deterministically; packages are versioned."""
import hashlib, io, json, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def build():
    rows = []
    for plugin in sorted((ROOT / 'plugins').iterdir()):
        meta = json.loads((plugin / '.claude-plugin/plugin.json').read_text())
        name, version = meta['name'], meta['version']
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w', compression=zipfile.ZIP_STORED, compresslevel=9) as archive:
            for path in sorted(plugin.rglob('*')):
                if not path.is_file(): continue
                if path.is_symlink(): raise ValueError('symlinks are not package sources')
                info = zipfile.ZipInfo(str(Path(name) / path.relative_to(plugin)), date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_STORED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        content = data.getvalue(); digest = hashlib.sha256(content).hexdigest()
        relative = f'packages/{name}/{version}/plugin.zip'
        target = ROOT / relative; target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != content:
            raise ValueError(f'{relative} already exists with different bytes; bump version')
        target.write_bytes(content)
        rows.append({'name': name, 'version': version, 'category': 'developer-tools',
            'description': 'XHarness GitHub CLI workflows for commits, pull requests, issues, releases, Actions, secrets, repositories, Gists and Codespaces.',
            'description_i18n': {'zh-CN': 'XHarness 原创 GitHub CLI 技能，覆盖提交、PR、Issue、发布、CI、Secret、仓库、Gist 和 Codespaces。'},
            'source': {'source': 'url', 'type': 'zip',
                'url': f'https://raw.githubusercontent.com/123123213weqw/xharness-plugin-registry/main/{relative}',
                'mirrors': [f'https://gitee.com/wangyue2006/xharness-plugin-registry/raw/main/{relative}'], 'sha256': digest}})
    (ROOT / 'catalog.json').write_text(json.dumps({'plugins': rows}, indent=2, ensure_ascii=False) + '\n')
if __name__ == '__main__': build()
