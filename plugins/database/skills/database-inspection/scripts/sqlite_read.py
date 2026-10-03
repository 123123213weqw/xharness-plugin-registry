#!/usr/bin/env python3
"""Bounded read-only SQLite inspection; Python 3.11+ with sqlite3 required."""
import argparse, base64, json, math, sqlite3, time
from pathlib import Path

def cell(value):
    if isinstance(value, bytes):
        return {'base64':base64.b64encode(value[:4096]).decode('ascii'),'bytes':len(value),'truncated':len(value)>4096}
    if isinstance(value, str) and len(value.encode('utf-8'))>4096:
        return {'text':value.encode('utf-8')[:4096].decode('utf-8',errors='replace'),'truncated':True}
    return value

def read(database, action='inspect', sql=None, params=(), max_rows=100, timeout=3):
    if not 1 <= max_rows <= 1000 or not math.isfinite(timeout) or not 0 < timeout <= 30: raise ValueError('invalid bounds')
    path = Path(database).resolve(strict=True)
    if not path.is_file(): raise ValueError('database must be an existing file')
    if action not in ('inspect','query','explain'): raise ValueError('unsupported action')
    if action == 'inspect': sql = "SELECT name,type,sql FROM sqlite_schema WHERE type IN ('table','view','index') AND name NOT LIKE 'sqlite_%' ORDER BY name"
    elif not isinstance(sql,str) or not sql.strip(): raise ValueError('SQL is required')
    if action == 'explain': sql = 'EXPLAIN QUERY PLAN ' + sql
    if len(sql.encode('utf-8')) > 65536: raise ValueError('SQL too large')
    deadline = time.monotonic() + timeout
    connection = sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=timeout)
    try:
        if not hasattr(connection, 'setlimit'): raise ValueError('Python 3.11+ required')
        connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH,1024*1024)
        connection.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH,65536)
        connection.execute('PRAGMA query_only=ON')
        allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_RECURSIVE}
        def authorize(code,a,b,db,trigger):
            if code not in allowed: return sqlite3.SQLITE_DENY
            if code == sqlite3.SQLITE_FUNCTION and str(b or a).lower() in {'load_extension','writefile','readfile'}: return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        connection.set_authorizer(authorize)
        connection.set_progress_handler(lambda: int(time.monotonic() >= deadline),1000)
        cursor=connection.execute(sql,params)
        columns=[entry[0] for entry in cursor.description or []]
        rows=[]; total=0; truncated=False
        for _ in range(max_rows+1):
            row=cursor.fetchone()
            if row is None: break
            values=[cell(value) for value in row]
            size=len(json.dumps(values,ensure_ascii=False).encode('utf-8'))
            if len(rows)==max_rows or total+size>256*1024: truncated=True;break
            rows.append(values);total+=size
        return {'ok':True,'engine':'sqlite','read_only':True,'columns':columns,'rows':rows,
                'truncated':truncated,'value_truncated':any(isinstance(v,dict) and v.get('truncated') for row in rows for v in row)}
    finally:
        connection.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('database');p.add_argument('action',choices=['inspect','query','explain'])
    p.add_argument('--sql');p.add_argument('--params-json',default='[]');p.add_argument('--max-rows',type=int,default=100);p.add_argument('--timeout',type=float,default=3)
    args=p.parse_args()
    try:
        params=json.loads(args.params_json)
        if not isinstance(params,(list,dict)): raise ValueError('parameters must be array/object')
        result=read(args.database,args.action,args.sql,params,args.max_rows,args.timeout)
    except (sqlite3.Error,ValueError,OSError,UnicodeError) as error:
        result={'ok':False,'kind':'database_error' if isinstance(error,sqlite3.Error) else 'input_error','error':type(error).__name__,'read_only':True}
    print(json.dumps(result,ensure_ascii=False));return 0 if result['ok'] else 1
if __name__=='__main__': raise SystemExit(main())
