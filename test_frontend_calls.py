#!/usr/bin/env python3
import json, time, re
from urllib import request as urllib_request
from urllib import parse as urllib_parse

BASE = "http://127.0.0.1:8000"
TIMEOUT = 5


def safe_username_from_name(name):
    safe = re.sub(r"[^a-z0-9]+", '.', name.lower())
    safe = re.sub(r"^\.+|\.+$", '', safe)
    if not safe:
        safe = 'employee'
    return f"{safe}.{str(int(time.time()))[-4:]}"


def do_request(method, path, headers=None, data=None, is_json=False):
    url = BASE + path
    hdrs = headers.copy() if headers else {}
    body = None
    if data is not None:
        if is_json:
            body = json.dumps(data).encode('utf-8')
            hdrs.setdefault('Content-Type', 'application/json')
        else:
            body = urllib_parse.urlencode(data).encode('utf-8')
            hdrs.setdefault('Content-Type', 'application/x-www-form-urlencoded')
    req = urllib_request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib_request.urlopen(req, timeout=TIMEOUT) as resp:
            status = resp.getcode()
            raw = resp.read().decode('utf-8')
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = raw
            print(f"{method} {path} -> {status}\n{parsed}\n---")
            return status, parsed
    except Exception as e:
        print(f"{method} {path} -> EXCEPTION: {e}\n---")
        return 'ERR', str(e)


if __name__ == '__main__':
    # 1) GET list (quick check)
    do_request('GET', '/employees?skip=0&limit=1')

    # 2) Login as admin via form
    status, resp = do_request('POST', '/auth/login', data={'username': 'admin', 'password': 'password123'}, is_json=False)
    token = None
    if status != 'ERR' and isinstance(resp, dict) and 'access_token' in resp:
        token = resp['access_token']
    auth_headers = {}
    if token:
        auth_headers['Authorization'] = f"Bearer {token}"

    # 3) Create via frontend-like payload generator
    name = 'Frontend Test User'
    safe_username = safe_username_from_name(name)
    new_emp = {
        'full_name': name,
        'position': 'QA',
        'role': 'receptionist',
        'username': safe_username,
        'password': 'password123'
    }
    status, resp = do_request('POST', '/employees', headers=auth_headers, data=new_emp, is_json=True)
    created_id = None
    if status != 'ERR' and isinstance(resp, dict):
        created_id = resp.get('id') or resp.get('employee_id')

    # 4) Update
    if created_id:
        update_body = {'full_name': 'Frontend Test User Updated'}
        do_request('PUT', f'/employees/{created_id}', headers=auth_headers, data=update_body, is_json=True)

        # 5) Get
        do_request('GET', f'/employees/{created_id}', headers=auth_headers)

        # 6) Delete
        do_request('DELETE', f'/employees/{created_id}', headers=auth_headers)
    else:
        print('Creation failed; skipping update/get/delete')

    print('\nDone.')
