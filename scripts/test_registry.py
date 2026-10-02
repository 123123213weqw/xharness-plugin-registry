#!/usr/bin/env python3
import hashlib, json, re, shutil, stat, tempfile, unittest, zipfile
from pathlib import Path, PurePosixPath
import build_catalog
ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'github':10,'git-pr-workflows':5,'pr-review':8,'unit-testing':4,
            'debugging':3,'refactoring':6,'documents':4,'browser':1}
SECRET = re.compile(rb'(?:sk-[0-9a-fA-F]{32}|gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
FORBIDDEN = {'.git','node_modules','target','__pycache__','spend.sqlite','.env'}
class RegistryTest(unittest.TestCase):
    def test_sources_and_archive(self):
        catalog = json.loads((ROOT/'catalog.json').read_bytes())
        self.assertEqual({p['name'] for p in catalog['plugins']}, set(EXPECTED))
        for p in catalog['plugins']:
            with self.subTest(plugin=p['name']):
                name=p['name']; source=p['source']; relative=f'packages/{name}/{p["version"]}/plugin.zip'
                self.assertEqual(source['url'], build_catalog.BASE+relative)
                self.assertEqual(source['mirrors'], [build_catalog.MIRROR+relative])
                self.assertTrue(p['descriptionI18n']['zh-CN'])
                self.assertTrue((ROOT/'icons'/Path(p['icon']).name).is_file())
                data=(ROOT/relative).read_bytes(); self.assertEqual(hashlib.sha256(data).hexdigest(), source['sha256'])
                self.assertLess(len(data), 64*1024*1024)
                with zipfile.ZipFile(ROOT/relative) as z:
                    names=z.namelist(); self.assertEqual(len(names),len(set(names))); self.assertIsNone(z.testzip())
                    self.assertEqual(len([n for n in names if n.endswith('/SKILL.md')]), EXPECTED[name])
                    self.assertIn(name+'/LICENSE',names); self.assertNotIn(name+'/.mcp.json',names)
                    self.assertNotIn(name+'/registry.json',names)
                    meta=json.loads(z.read(name+'/.claude-plugin/plugin.json'))
                    self.assertEqual((meta['name'],meta['version']),(name,p['version']))
                    for n in names:
                        path=PurePosixPath(n); self.assertFalse(path.is_absolute()); self.assertNotIn('..',path.parts)
                        self.assertTrue(n.startswith(name+'/'));self.assertFalse(FORBIDDEN.intersection(path.parts))
                        self.assertFalse(any(s.startswith('.env') for s in path.parts)); self.assertIsNone(SECRET.search(z.read(n)))
                        self.assertNotIn(b'/Users/wangyue/',z.read(n)); self.assertNotIn(b'/home/data/wangyue/',z.read(n))
                    if name!='github':
                        self.assertIn('-beta.',p['version']); self.assertIn(name+'/RELEASE.md',names)
                        self.assertIn(b'Opt-in beta',z.read(name+'/RELEASE.md'))
    def test_skill_references_exist(self):
        for p in (ROOT/'plugins').glob('*/skills/**/SKILL.md'):
            self.assertTrue(p.read_text().startswith('---\n'))
        for p in (ROOT/'plugins').glob('*/skills/**/*.md'):
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):
                if '://' in link or link.startswith(('#','mailto:')): continue
                target=(p.parent/link.split('#')[0]).resolve()
                self.assertTrue(target.is_relative_to((ROOT/'plugins'/p.relative_to(ROOT/'plugins').parts[0]).resolve()),str(p))
                self.assertTrue(target.is_file(),str(p)+' -> '+link)
    def test_stable_github_unchanged(self):
        data=(ROOT/'packages/github/0.2.0/plugin.zip').read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),'2f1b40aadb5d8ee52af7e678f85fa7ab836f8835202e86c22ee388e3e98f9ab5')
    def test_beta_release_provenance(self):
        for name in set(EXPECTED)-{'github'}:
            plugin=ROOT/'plugins'/name
            provenance=json.loads((plugin/'provenance.json').read_bytes())
            self.assertEqual(provenance['release_channel'],'beta')
            self.assertIs(provenance['full_source_platform_or_license_equivalence_claimed'],False)
            actual={p.relative_to(plugin).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in plugin.rglob('*') if p.is_file()
                and p.relative_to(plugin).as_posix() not in {'registry.json','provenance.json'}
                and '__pycache__' not in p.parts and p.suffix!='.pyc'}
            self.assertEqual(provenance['release_file_sha256'],actual,name)
    def test_determinism(self):
        before={p:p.read_bytes() for p in ROOT.glob('packages/*/*/plugin.zip')}
        catalog=(ROOT/'catalog.json').read_bytes(); build_catalog.build()
        self.assertEqual((ROOT/'catalog.json').read_bytes(),catalog)
        self.assertEqual({p:p.read_bytes() for p in before},before)
    def test_version_immutability(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);shutil.copytree(ROOT/'plugins',d/'plugins');shutil.copytree(ROOT/'packages',d/'packages')
            (d/'plugins/browser/skills/browser-workflow/SKILL.md').write_text('changed')
            old=(d/'packages/browser/0.1.0-beta.1/plugin.zip').read_bytes()
            with self.assertRaisesRegex(ValueError,'bump version'):build_catalog.build(d)
            self.assertEqual((d/'packages/browser/0.1.0-beta.1/plugin.zip').read_bytes(),old)
if __name__=='__main__': unittest.main()
