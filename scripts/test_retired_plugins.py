#!/usr/bin/env python3
"""Public-store retirement contracts; never uninstall user-owned private plugins."""
import json,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RETIRED={'api-testing','browser','database','debugging','docker','documents','git-pr-workflows','github','pr-review','refactoring','unit-testing'}
class RetirementTest(unittest.TestCase):
    def test_only_wordcraft_has_public_sources(self):
        self.assertEqual({p.name for p in (ROOT/'plugins').iterdir() if p.is_dir()},{'wordcraft'})
    def test_only_wordcraft_has_downloadable_packages(self):
        self.assertEqual({p.name for p in (ROOT/'packages').iterdir() if p.is_dir()},{'wordcraft'})
    def test_retired_sources_and_packages_are_absent(self):
        for name in RETIRED:
            with self.subTest(name=name):
                self.assertFalse((ROOT/'plugins'/name).exists());self.assertFalse((ROOT/'packages'/name).exists())
    def test_catalog_has_one_reviewed_editor(self):
        rows=json.loads((ROOT/'catalog.json').read_text())['plugins']
        self.assertEqual([p['name'] for p in rows],['wordcraft'])
        self.assertEqual(rows[0]['version'],'0.1.0')
        self.assertEqual(rows[0]['source']['sha256'],'ed0879f7548b1ce7e7a4920f2b89a0d55fbac0e70ffa365a52d9d983a749e22d')
    def test_no_unreferenced_store_icons(self):
        self.assertEqual({p.name for p in (ROOT/'icons').iterdir() if p.is_file()},{'wordcraft.svg'})
        row=json.loads((ROOT/'catalog.json').read_text())['plugins'][0]
        self.assertTrue(row['icon'].endswith('/icons/wordcraft.svg'))
    def test_kept_package_still_declares_real_editor_capabilities(self):
        with zipfile.ZipFile(ROOT/'packages/wordcraft/0.1.0/plugin.zip') as z:
            self.assertIn('wordcraft/.mcp.json',z.namelist());self.assertIn('wordcraft/.xharness-ui.json',z.namelist())
            self.assertIn('wordcraft/dist/tools.json',z.namelist())
if __name__=='__main__':unittest.main()
