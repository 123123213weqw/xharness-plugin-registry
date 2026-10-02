#!/usr/bin/env python3
"""Read-only Git/index/worktree anchors; no commit/stage/reset/push operations."""
import argparse,subprocess,json,hashlib,pathlib,os,stat
p=argparse.ArgumentParser();p.add_argument('repository',type=pathlib.Path);p.add_argument('--exclude-prefix',action='append',default=['.xharness/']);a=p.parse_args();repo=a.repository.resolve()
def git(*args):return subprocess.run(['git','-c','core.fsmonitor=false','-c','core.pager=cat','-C',str(repo),*args],check=True,capture_output=True,timeout=10,env={**{k:v for k,v in os.environ.items() if not k.startswith('GIT_')},'GIT_TERMINAL_PROMPT':'0','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_NO_REPLACE_OBJECTS':'1'}).stdout
root=pathlib.Path(git('rev-parse','--show-toplevel').decode().strip()).resolve();assert root==repo,'pass the actual repository root'
entries=[]
for record in git('ls-files','--stage','-z').split(b'\0'):
 if record:
  header,path=record.split(b'\t',1);mode,oid,stage=header.decode().split();entries.append({'path':path.decode(),'mode':mode,'oid':oid,'stage':int(stage)})
work={}
for raw in git('ls-files','--cached','--others','--exclude-standard','-z').split(b'\0'):
 if not raw:continue
 rel=raw.decode()
 if any(rel.startswith(prefix) for prefix in a.exclude_prefix):continue
 path=repo/rel
 if path.is_symlink():work[rel]={'symlink':os.readlink(path),'mode':stat.S_IMODE(path.lstat().st_mode)}
 elif path.is_file():work[rel]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':stat.S_IMODE(path.stat().st_mode)}
 else:work[rel]={'missing_or_nonregular':True}
print(json.dumps({'root':str(repo),'head':git('rev-parse','HEAD').decode().strip(),'branch':git('branch','--show-current').decode().strip(),'index':entries,'worktree':work},sort_keys=True,indent=2))
