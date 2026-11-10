#!/usr/bin/env python3
"""Parse the retained archive's JavaScript without running the plugin or WASM."""
from pathlib import Path
import subprocess,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp,zipfile.ZipFile(ROOT/'packages/wordcraft/0.1.0/plugin.zip') as archive:
    for name in ('dist/launch.mjs','dist/server.mjs','dist/app.js'):
        # Use .mjs for browser ES modules as well; this never imports/executes them.
        target=Path(tmp)/(Path(name).stem+'.mjs')
        target.write_bytes(archive.read('wordcraft/'+name))
        subprocess.run(['node','--check',str(target)],check=True)
        print('syntax checked:',name)
