#!/usr/bin/env python3
import json
import sys
import time
from urllib import request as urllib_request
from urllib import parse as urllib_parse

def try_parse_json(s):
    try:
        return json.loads(s)
    except Exception:
        return s

BASE = "http://127.0.0.1:8000"
TIMEOUT = 5

calls = []

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
            parsed = try_parse_json(raw)
            calls.append((method, path, status, parsed))
            print(f"{method} {path} -> {status}\n{parsed}\n---")
            return status, parsed
    except Exception as e:
        calls.append((method, path, 'ERR', str(e)))
        print(f"{method} {path} -> EXCEPTION: {e}\n---")
        return 'ERR', str(e)

if __name__ == '__main__':
    # 1) GET /employees?skip=0&limit=1
    do_request('GET', '/employees?skip=0&limit=1')

    # 2) POST /auth/login with form username=admin password=password123
    status, resp = do_request('POST', '/auth/login', data={'username':'admin','password':'password123'}, is_json=False)
    token = None
    if status != 'ERR' and isinstance(resp, dict) and 'access_token' in resp:
        token = resp['access_token']
    else:
        # maybe text response; leave token None
        pass

    auth_headers = {}
    if token:
        auth_headers['Authorization'] = f"Bearer {token}"

    # 3) POST /employees to create a test employee (use admin token)
    new_employee = {
        'full_name': 'Test Employee X',
        'position': 'Tester',
        'username': f'test_user_{int(time.time())}',
        'password': 'testpass',
        'role': 'receptionist'
    }
    status, resp = do_request('POST', '/employees', headers=auth_headers, data=new_employee, is_json=True)
    created_id = None
    if status != 'ERR' and isinstance(resp, dict) and 'id' in resp:
        created_id = resp['id']
    elif status != 'ERR' and isinstance(resp, dict) and 'employee_id' in resp:
        created_id = resp['employee_id']

    # 4) PUT /employees/{id} to update full_name
    if created_id:
        update_body = {'full_name': 'Test Employee X Updated'}
        do_request('PUT', f'/employees/{created_id}', headers=auth_headers, data=update_body, is_json=True)

        # 5) GET /employees/{id} to confirm
        do_request('GET', f'/employees/{created_id}', headers=auth_headers)

        # 6) DELETE /employees/{id}
        do_request('DELETE', f'/employees/{created_id}', headers=auth_headers)
    else:
        print('Skipping update/get/delete because employee creation failed or no token.')

    # concise summary
    print('\nSUMMARY:')
    for method, path, status, body in calls:
        print(f"- {method} {path}: {status} -> {body}")

    # final outcome
    if created_id and token:
        print('\nFINAL: created employee id=' + str(created_id) + ' then updated, fetched, and deleted successfully (if no errors above).')
    else:
        print('\nFINAL: sequence incomplete. See above for errors or missing token.')
