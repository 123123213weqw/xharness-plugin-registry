#!/usr/bin/env python3
"""Summarize captured Compose JSON/JSONL; never invokes Docker or mutates state."""
import argparse,json
from pathlib import Path
LIMIT=1024*1024
STATES={'paused','restarting','removing','running','dead','created','exited'}

def summarize(text):
    if len(text.encode('utf-8'))>LIMIT: raise ValueError('input exceeds 1 MiB')
    if not text.strip(): rows=[]
    else:
        try:
            value=json.loads(text)
            rows=value if isinstance(value,list) else [value]
        except json.JSONDecodeError: rows=[json.loads(line) for line in text.splitlines() if line.strip()]
    if len(rows)>10000: raise ValueError('too many observations')
    result=[]
    for row in rows:
        if not isinstance(row,dict): raise ValueError('container observation must be an object')
        name=row.get('Name');state=row.get('State');health=row.get('Health','');code=row.get('ExitCode')
        if not isinstance(name,str) or not name or not isinstance(state,str): raise ValueError('missing typed Name/State')
        if not isinstance(health,str) or code is not None and (isinstance(code,bool) or not isinstance(code,int)): raise ValueError('invalid Health/ExitCode')
        issue=state=='dead' or health=='unhealthy' or state=='exited' and code is not None and code!=0
        result.append({'name':name,'state':state,'known_state':state in STATES,'health':health or 'not_reported',
                       'exit_code':code,'issue_observed':issue,'readiness_verified':False})
    return {'ok':True,'containers':result,'observed_count':len(result),'issues_observed':sum(row['issue_observed'] for row in result),
            'readiness_verified':False,'empty_is_healthy':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');args=p.parse_args()
    try:
        with Path(args.input).open('rb') as stream: data=stream.read(LIMIT+1)
        if len(data)>LIMIT: raise ValueError('input exceeds 1 MiB')
        result=summarize(data.decode('utf-8-sig'))
    except (ValueError,OSError,UnicodeError) as error:result={'ok':False,'kind':'input_error','error':type(error).__name__}
    print(json.dumps(result,ensure_ascii=False));return 0 if result['ok'] else 1
if __name__=='__main__': raise SystemExit(main())
