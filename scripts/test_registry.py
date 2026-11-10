#!/usr/bin/env python3
import hashlib, json, re, shutil, stat, tempfile, unittest, zipfile
from pathlib import Path, PurePosixPath
import build_catalog
ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'wordcraft':1}
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
                    self.assertIn(name+'/LICENSE',names); self.assertEqual(name+'/.mcp.json' in names,name=='wordcraft')
                    self.assertNotIn(name+'/registry.json',names)
                    meta=json.loads(z.read(name+'/.claude-plugin/plugin.json'))
                    self.assertEqual((meta['name'],meta['version']),(name,p['version']))
                    for n in names:
                        path=PurePosixPath(n); self.assertFalse(path.is_absolute()); self.assertNotIn('..',path.parts)
                        self.assertTrue(n.startswith(name+'/'));self.assertFalse(FORBIDDEN.intersection(path.parts))
                        self.assertFalse(any(s.startswith('.env') for s in path.parts)); self.assertIsNone(SECRET.search(z.read(n)))
                        self.assertNotIn(b'/Users/wangyue/',z.read(n)); self.assertNotIn(b'/home/data/wangyue/',z.read(n))
                    if name not in {'github','wordcraft'}:
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
    def test_retained_wordcraft_archive_unchanged(self):
        data=(ROOT/'packages/wordcraft/0.1.0/plugin.zip').read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),'ed0879f7548b1ce7e7a4920f2b89a0d55fbac0e70ffa365a52d9d983a749e22d')
    def test_determinism(self):
        before={p:p.read_bytes() for p in ROOT.glob('packages/*/*/plugin.zip')}
        catalog=(ROOT/'catalog.json').read_bytes(); build_catalog.build()
        self.assertEqual((ROOT/'catalog.json').read_bytes(),catalog)
        self.assertEqual({p:p.read_bytes() for p in before},before)
    def test_version_immutability(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);plugin=root/'plugins/demo';(plugin/'.claude-plugin').mkdir(parents=True)
            (plugin/'.claude-plugin/plugin.json').write_text(json.dumps({'name':'demo','version':'1.0.0'}))
            (plugin/'registry.json').write_text(json.dumps({'description':'isolated test fixture'}))
            (plugin/'README.md').write_text('original fixture')
            build_catalog.build(root)
            archive=root/'packages/demo/1.0.0/plugin.zip';old=archive.read_bytes()
            (plugin/'README.md').write_text('changed fixture')
            with self.assertRaisesRegex(ValueError,'bump version'):build_catalog.build(root)
            self.assertEqual(archive.read_bytes(),old)
class WordCraftPrebuiltTest(unittest.TestCase):
    def test_missing_or_changed_archive_cannot_rebuild_or_overwrite_a_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); plugin=root/'wordcraft';shutil.copytree(ROOT/'plugins/wordcraft',plugin)
            target=root/'plugin.zip'
            with self.assertRaisesRegex(ValueError,'missing pinned'):build_catalog.verified_prebuilt(plugin,target,'wordcraft','0.1.0')
            target.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'archive changed'):build_catalog.verified_prebuilt(plugin,target,'wordcraft','0.1.0')
            self.assertEqual(target.read_bytes(),b'changed')
    def test_prebuilt_package_and_reviewed_metadata_are_both_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin=Path(tmp)/'wordcraft';shutil.copytree(ROOT/'plugins/wordcraft',plugin)
            target=ROOT/'packages/wordcraft/0.1.0/plugin.zip'
            (plugin/'RELEASE.md').write_text('unreviewed instructions')
            with self.assertRaisesRegex(ValueError,'review metadata mismatch'):build_catalog.verified_prebuilt(plugin,target,'wordcraft','0.1.0')
    def test_wordcraft_is_only_optional_stdio_with_reserved_workspace(self):
        with zipfile.ZipFile(ROOT/'packages/wordcraft/0.1.0/plugin.zip') as archive:
            config=json.loads(archive.read('wordcraft/.mcp.json'))
            self.assertEqual(config,{'mcpServers':{'wordcraft':{'type':'stdio','command':'node','args':['${PLUGIN_ROOT}/dist/launch.mjs']}}})
            launcher=archive.read('wordcraft/dist/launch.mjs')
            self.assertIn(b'XHARNESS_PLUGIN_WORKSPACE',launcher)
            self.assertNotIn(b'http:',launcher)
            self.assertIn(b'No default enablement or host restart',archive.read('wordcraft/RELEASE.md'))

if __name__=='__main__': unittest.main()
