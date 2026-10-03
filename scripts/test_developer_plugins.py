#!/usr/bin/env python3
"""Offline acceptance: loopback HTTP, actual read-only SQLite, captured Compose observations."""
import hashlib, http.server, importlib.util, json, os, socket, sqlite3, subprocess, sys, tempfile, threading, time, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
PATHS={
 'api': ROOT/'plugins/api-testing/skills/api-contract/scripts/api_tool.py',
 'db': ROOT/'plugins/database/skills/database-inspection/scripts/sqlite_read.py',
 'docker': ROOT/'plugins/docker/skills/compose-inspection/scripts/compose_state.py'}
def module(name):
    spec=importlib.util.spec_from_file_location(name,PATHS[name]); result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
api,db,docker=(module(name) for name in ('api','db','docker'))
def cli(name,*args):
    result=subprocess.run([sys.executable,str(PATHS[name]),*map(str,args)],capture_output=True,text=True,timeout=10)
    assert result.stderr=='',result.stderr
    return result.returncode,json.loads(result.stdout)
class Handler(http.server.BaseHTTPRequestHandler):
    requests=[]
    def log_message(self,*args):pass
    def do_HEAD(self):self.send_response(200);self.end_headers()
    def do_GET(self):
        self.requests.append(self.path)
        if self.path=='/slow': time.sleep(.12)
        if self.path=='/redirect':
            self.send_response(302);self.send_header('Location','/target');self.end_headers();return
        if self.path=='/broken':
            self.send_response(200);self.send_header('Content-Length','10000');self.end_headers();self.wfile.write(b'partial');self.close_connection=True;return
        body=(self.headers.get('Authorization','') if self.path=='/echo' else 'x'*200 if self.path=='/large' else '{"answer":42}').encode()
        self.send_response(503 if self.path=='/error' else 200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers()
        try:self.wfile.write(body)
        except (BrokenPipeError,ConnectionResetError):pass
class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.worker=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.worker.start();cls.url=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.worker.join(2)
    def test_contract_index(self):
        r=api.index({'openapi':'3.1.0','paths':{'/a':{'get':{'operationId':'find','responses':{'200':{}}}},'/b':{'$ref':'other.json'}}})
        self.assertEqual(r['operations'][0]['method'],'GET');self.assertEqual(r['unresolved_path_items'],['/b']);self.assertFalse(r['schema_validation_performed'])
    def test_invalid_contract(self):
        for value in (None,{}, {'openapi':'2.0.0','paths':{}},{'openapi':'3.1.0','paths':{'bad':{}}},{'openapi':'3.1.0','paths':{'/':{'get':[]}}}):
            with self.subTest(value=value),self.assertRaises(ValueError):api.index(value)
    def test_success_and_head(self):
        r=api.probe(self.url);self.assertTrue(r['ok']);self.assertEqual(json.loads(r['body'])['answer'],42);self.assertTrue(r['body_complete'])
        self.assertEqual(api.probe(self.url,'HEAD')['body'],'')
    def test_http_failure_not_success(self):
        r=api.probe(self.url+'/error');self.assertFalse(r['ok']);self.assertEqual(r['status'],503);self.assertEqual(r['kind'],'http_response')
    def test_redirect_not_followed(self):
        before=Handler.requests.count('/target');r=api.probe(self.url+'/redirect');self.assertEqual(r['status'],302);self.assertFalse(r['ok']);self.assertEqual(Handler.requests.count('/target'),before)
    def test_truncation(self):
        r=api.probe(self.url+'/large',limit=20);self.assertEqual(len(r['body']),20);self.assertTrue(r['truncated']);self.assertFalse(r['body_complete']);self.assertFalse(r['ok'])
    def test_broken_body(self):
        r=api.probe(self.url+'/broken');self.assertFalse(r['ok']);self.assertFalse(r['body_complete']);self.assertEqual(r['kind'],'body_read_error')
    def test_timeout(self):
        r=api.probe(self.url+'/slow',timeout=.02);self.assertFalse(r['ok']);self.assertEqual(r['kind'],'transport_error')
    def test_connection_refused(self):
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        self.assertFalse(api.probe(f'http://127.0.0.1:{port}',timeout=.1)['ok'])
    def test_redaction_and_bindings(self):
        with patch.dict(os.environ,{'TEST_API_AUTH':'Bearer synthetic-secret'}):
            r=api.probe(self.url+'/echo',header_env=['Authorization=TEST_API_AUTH']);self.assertEqual(r['body'],'[REDACTED]')
            for values in (['Authorization=MISSING_TEST_AUTH_ABC'],['Authorization=TEST_API_AUTH','authorization=TEST_API_AUTH'],['Invalid Header=TEST_API_AUTH']):
                with self.subTest(values=values),self.assertRaises(ValueError):api.probe(self.url,header_env=values)
        with patch.dict(os.environ,{'TEST_API_AUTH':'bad\nheader'}),self.assertRaises(ValueError):api.probe(self.url,header_env=['Authorization=TEST_API_AUTH'])
    def test_invalid_requests(self):
        for kwargs in ({'url':'file:///tmp/x'},{'url':'http://u:p@example.com'},{'method':'POST'},{'limit':0},{'timeout':float('nan')}):
            params={'url':self.url};params.update(kwargs)
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):api.probe(**params)
    def test_cli_exit_status(self):
        self.assertEqual(cli('api','probe',self.url)[0],0);self.assertEqual(cli('api','probe',self.url+'/error')[0],1)
    def test_bounded_file(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'spec.json';p.write_bytes(b'x'*(api.LIMIT+1))
            self.assertEqual(cli('api','index',p)[0],1)
class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'数据库 # ?.db'
        with sqlite3.connect(self.path) as c:
            c.execute('CREATE TABLE items(id INTEGER PRIMARY KEY,value TEXT)');c.executemany('INSERT INTO items VALUES(?,?)',[(1,'a'),(2,'b'),(3,'c')])
        self.before=hashlib.sha256(self.path.read_bytes()).hexdigest()
    def tearDown(self):
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(),self.before);self.temp.cleanup()
    def test_inspect_actual_database(self):
        r=db.read(self.path);self.assertTrue(r['read_only']);self.assertEqual(r['rows'][0][0],'items')
    def test_bound_parameters(self):
        r=db.read(self.path,'query','SELECT value FROM items WHERE id=?',[2]);self.assertEqual(r['rows'],[['b']])
        r=db.read(self.path,'query','SELECT value FROM items WHERE id=:id',{'id':1});self.assertEqual(r['rows'],[['a']])
    def test_duplicate_columns_preserved(self):
        r=db.read(self.path,'query','SELECT 1 AS a,2 AS a');self.assertEqual(r['columns'],['a','a']);self.assertEqual(r['rows'],[[1,2]])
    def test_cte_and_explain(self):
        self.assertEqual(db.read(self.path,'query','WITH q AS (SELECT 1 AS v) SELECT v FROM q')['rows'],[[1]])
        self.assertTrue(db.read(self.path,'explain','SELECT * FROM items WHERE id=1')['rows'])
    def test_writes_and_escape_denied(self):
        for sql in ("INSERT INTO items VALUES(4,'d')",'DELETE FROM items','DROP TABLE items','CREATE TABLE nope(x)',"ATTACH DATABASE ':memory:' AS other",'PRAGMA journal_mode=WAL','SELECT load_extension(\'missing\')','SELECT 1; SELECT 2','BEGIN'):
            with self.subTest(sql=sql),self.assertRaises(sqlite3.Error):db.read(self.path,'query',sql)
        # Error paths release connection resources: immediate writer lock still works.
        with sqlite3.connect(self.path,timeout=.1) as c:c.execute('BEGIN IMMEDIATE');c.rollback()
    def test_missing_database_not_created(self):
        path=self.path.parent/'missing.db'
        with self.assertRaises(FileNotFoundError):db.read(path)
        self.assertFalse(path.exists())
    def test_rows_bounded(self):
        r=db.read(self.path,'query','SELECT * FROM items',max_rows=1);self.assertEqual(len(r['rows']),1);self.assertTrue(r['truncated'])
    def test_large_cells_and_blobs(self):
        r=db.read(self.path,'query',"SELECT printf('%.*c',10000,'a'),zeroblob(5000)")
        self.assertTrue(r['value_truncated']);self.assertTrue(r['rows'][0][0]['truncated']);self.assertEqual(r['rows'][0][1]['bytes'],5000)
    def test_engine_allocation_limit(self):
        with self.assertRaises(sqlite3.Error):db.read(self.path,'query','SELECT zeroblob(2000000)')
    def test_recursive_deadline(self):
        start=time.monotonic()
        with self.assertRaises(sqlite3.OperationalError):db.read(self.path,'query','WITH RECURSIVE q(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM q) SELECT sum(n) FROM q',timeout=.03)
        self.assertLess(time.monotonic()-start,2)
    def test_invalid_bounds(self):
        for kwargs in ({'max_rows':0},{'timeout':float('inf')},{'action':'write'},{'action':'query','sql':''}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):db.read(self.path,**kwargs)
    def test_cli_status(self):
        self.assertEqual(cli('db',self.path,'inspect')[0],0)
        code,r=cli('db',self.path,'query','--sql','DELETE FROM items');self.assertEqual(code,1);self.assertEqual(r['kind'],'database_error')
        self.assertEqual(cli('db',self.path,'query','--sql','SELECT 1','--params-json','null')[0],1)
class DockerTest(unittest.TestCase):
    def test_jsonl_and_array(self):
        rows=[{'Name':'example-bar-1','State':'exited','Health':'','ExitCode':0},{'Name':'example-foo-1','State':'running','Health':'','ExitCode':0}]
        a=docker.summarize(json.dumps(rows));b=docker.summarize('\n'.join(json.dumps(row) for row in rows));self.assertEqual(a,b);self.assertEqual(a['issues_observed'],0);self.assertFalse(a['readiness_verified'])
    def test_failure_states(self):
        rows=[{'Name':'a','State':'dead'},{'Name':'b','State':'running','Health':'unhealthy'},{'Name':'c','State':'exited','ExitCode':1}]
        self.assertEqual(docker.summarize(json.dumps(rows))['issues_observed'],3)
    def test_unknown_state_not_invented(self):
        r=docker.summarize('{"Name":"a","State":"future"}');self.assertFalse(r['containers'][0]['known_state']);self.assertFalse(r['readiness_verified'])
    def test_no_observations_not_healthy(self):
        for text in ('',' \n ','[]'):
            r=docker.summarize(text);self.assertEqual(r['observed_count'],0);self.assertFalse(r['empty_is_healthy'])
    def test_secret_fields_omitted(self):
        r=docker.summarize('{"Name":"a","State":"running","Command":"secret-password","Environment":{"KEY":"private"}}');self.assertNotIn('secret-password',json.dumps(r));self.assertNotIn('private',json.dumps(r))
    def test_malformed_input(self):
        for value in ('{','null','[1]','{}','{"Name":"a","State":"running","ExitCode":true}','{"Name":"a","State":"running","ExitCode":"0"}','{"Name":"a","State":"running","Health":{}}'):
            with self.subTest(value=value),self.assertRaises(ValueError):docker.summarize(value)
    def test_limits(self):
        with self.assertRaises(ValueError):docker.summarize(' '* (docker.LIMIT+1))
        with self.assertRaises(ValueError):docker.summarize(json.dumps([{'Name':'a','State':'running'}]*10001))
    def test_cli_bom_and_error_status(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'observations.json';path.write_text('[{"Name":"a","State":"running"}]',encoding='utf-8-sig');self.assertEqual(cli('docker',path)[0],0)
            path.write_text('{');self.assertEqual(cli('docker',path)[0],1)
            path.write_bytes(b'x'*(docker.LIMIT+1));self.assertEqual(cli('docker',path)[0],1)
if __name__=='__main__':unittest.main(verbosity=2)
