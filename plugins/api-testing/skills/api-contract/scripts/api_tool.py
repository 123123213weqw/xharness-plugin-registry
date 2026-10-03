#!/usr/bin/env python3
"""Bounded OpenAPI JSON index and read-only HTTP probe; stdlib, no shell."""
import argparse, http.client, json, math, os, re, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
LIMIT = 1024 * 1024
METHODS = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'}

def load_json(path):
    with Path(path).open('rb') as stream: data = stream.read(LIMIT + 1)
    if len(data) > LIMIT: raise ValueError('document exceeds 1 MiB')
    return json.loads(data.decode('utf-8-sig'))

def index(document):
    if not isinstance(document, dict) or not re.fullmatch(r'3\.\d+\.\d+(?:[-+].*)?', str(document.get('openapi', ''))):
        raise ValueError('expected a JSON OpenAPI 3.x document')
    paths = document.get('paths')
    if not isinstance(paths, dict): raise ValueError('paths must be an object')
    rows, unresolved = [], []
    for path, item in paths.items():
        if not path.startswith('/') or not isinstance(item, dict): raise ValueError('invalid Path Item')
        if '$ref' in item: unresolved.append(path)
        for method, operation in item.items():
            if method not in METHODS: continue
            if not isinstance(operation, dict): raise ValueError('operation must be an object')
            responses = operation.get('responses')
            if not isinstance(responses, dict): raise ValueError('responses must be an object')
            rows.append({'method': method.upper(), 'path': path, 'operation_id': operation.get('operationId'),
                         'response_statuses': sorted(responses), 'has_request_body': 'requestBody' in operation})
    return {'ok': True, 'openapi': document['openapi'], 'operations': rows,
            'unresolved_path_items': unresolved, 'schema_validation_performed': False}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url): return None

def probe(url, method='GET', timeout=15, limit=65536, header_env=()):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('URL must be HTTP(S) without embedded credentials')
    if method not in ('GET', 'HEAD'): raise ValueError('probe supports only GET and HEAD')
    if not math.isfinite(timeout) or not 0 < timeout <= 120 or not 1 <= limit <= LIMIT: raise ValueError('invalid bounds')
    headers, secrets, seen = {}, [], set()
    for binding in header_env:
        if '=' not in binding: raise ValueError('header binding must be Header=ENV_NAME')
        key, env = binding.split('=', 1)
        if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", key) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', env):
            raise ValueError('invalid header binding')
        if key.lower() in seen: raise ValueError('duplicate header binding')
        value = os.environ.get(env)
        if not value or '\r' in value or '\n' in value: raise ValueError('missing or invalid header environment')
        headers[key] = value; secrets.append(value); seen.add(key.lower())
    start = time.monotonic()
    request = urllib.request.Request(url, headers=headers, method=method)
    try: response = urllib.request.build_opener(NoRedirect).open(request, timeout=timeout)
    except urllib.error.HTTPError as error: response = error
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
        return {'ok': False, 'kind': 'transport_error', 'outcome': 'no_complete_http_response', 'elapsed_ms': round((time.monotonic()-start)*1000)}
    try:
        with response:
            status = response.code
            declared_length = response.headers.get('Content-Length')
            expected = int(declared_length) if declared_length and declared_length.isdecimal() else None
            raw = response.read(limit + 1)
            if method != 'HEAD' and expected is not None and len(raw) < expected and len(raw) <= limit:
                return {'ok': False, 'kind': 'body_read_error', 'status': status, 'body_complete': False}
            media = response.headers.get_content_type()
    except (TimeoutError, OSError, ValueError, http.client.HTTPException):
        return {'ok': False, 'kind': 'body_read_error', 'status': status, 'body_complete': False}
    truncated = len(raw) > limit
    text = raw[:limit].decode('utf-8', errors='replace')
    for secret in secrets: text = text.replace(secret, '[REDACTED]')
    # A fragment is text, never reported as complete/valid JSON.
    return {'ok': 200 <= status < 300 and not truncated, 'kind': 'http_response', 'status': status,
            'content_type': media, 'body': text, 'truncated': truncated, 'body_complete': not truncated,
            'elapsed_ms': round((time.monotonic()-start)*1000), 'schema_validation_performed': False}

def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('index'); p.add_argument('spec')
    p = sub.add_parser('probe'); p.add_argument('url'); p.add_argument('--method', choices=['GET','HEAD'], default='GET')
    p.add_argument('--timeout', type=float, default=15); p.add_argument('--max-bytes', type=int, default=65536)
    p.add_argument('--header-env', action='append', default=[])
    args = parser.parse_args()
    try: result = index(load_json(args.spec)) if args.action == 'index' else probe(args.url,args.method,args.timeout,args.max_bytes,args.header_env)
    except (ValueError, OSError, UnicodeError) as error: result = {'ok': False, 'kind': 'input_error', 'error': type(error).__name__}
    print(json.dumps(result, ensure_ascii=False)); return 0 if result['ok'] else 1
if __name__ == '__main__': raise SystemExit(main())
