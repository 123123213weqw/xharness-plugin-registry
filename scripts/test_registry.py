#!/usr/bin/env python3
import hashlib, json, tempfile, unittest, zipfile
from pathlib import Path
from urllib.parse import urlparse
import build_catalog
ROOT = Path(__file__).resolve().parents[1]
class RegistryTest(unittest.TestCase):
    def test_sources_and_archive(self):
        catalog = json.loads((ROOT / 'catalog.json').read_text())
        self.assertEqual([p['name'] for p in catalog['plugins']], ['github'])
        for p in catalog['plugins']:
            source = p['source']; relative = f"packages/{p['name']}/{p['version']}/plugin.zip"
            self.assertEqual(source['url'], f'https://raw.githubusercontent.com/123123213weqw/xharness-plugin-registry/main/{relative}')
            self.assertEqual(source['mirrors'], [f'https://gitee.com/wangyue2006/xharness-plugin-registry/raw/main/{relative}'])
            data = (ROOT / relative).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), source['sha256'])
            with zipfile.ZipFile(ROOT / relative) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(len([n for n in z.namelist() if n.endswith('/SKILL.md')]), 10)
                self.assertTrue(all(n.startswith(p['name']+'/') and '..' not in n.split('/') for n in z.namelist()))
                self.assertIn(p['name']+'/LICENSE', z.namelist())
                self.assertNotIn(p['name']+'/.mcp.json', z.namelist())
                for n in z.namelist():
                    self.assertNotIn('.env', Path(n).parts)
                    self.assertNotIn('sk-', z.read(n).decode('utf-8'))
    def test_determinism(self):
        before = {p: p.read_bytes() for p in ROOT.glob('packages/*/*/plugin.zip')}
        catalog = (ROOT / 'catalog.json').read_bytes(); build_catalog.build()
        self.assertEqual((ROOT / 'catalog.json').read_bytes(), catalog)
        self.assertEqual({p: p.read_bytes() for p in before}, before)
if __name__ == '__main__': unittest.main()
