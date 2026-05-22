import urllib.request, urllib.parse, json
from datetime import date, timedelta

BASE = 'http://127.0.0.1:8000'


def req(method, path, data=None):
    url = BASE + path
    headers = {'Content-Type': 'application/json'}
    if data is not None:
        body = json.dumps(data).encode('utf-8')
    else:
        body = None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            text = r.read()
            if not text:
                return r.getcode(), None
            return r.getcode(), json.loads(text.decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, None
    except Exception as e:
        print('ERROR:', e)
        return None, None


def find_available_room(ci, co, exclude_ids=None):
    exclude_ids = exclude_ids or []
    code, rooms = req('GET', f'/rooms?check_in_date={ci.isoformat()}&check_out_date={co.isoformat()}')
    if code not in (200,) or not rooms:
        return None
    items = rooms.get('items') if isinstance(rooms, dict) and 'items' in rooms else rooms
    for r in items:
        rid = r.get('id') or r.get('room_id')
        if rid and rid not in exclude_ids:
            return rid
    return None

print('Running extended E2E scenarios against', BASE)

# Scenario 1: Full pay invoice
print('\n=== Scenario 1: Full pay invoice ===')
# Create guest
guest = {'full_name':'S1 Guest','email':f's1+{date.today().isoformat()}@example.com','phone':'0123456789'}
code,res = req('POST','/api/guests',guest)
print('create guest',code,res)
if code not in (200,201): raise SystemExit(1)
gid = res.get('id')
# choose room
code, rooms = req('GET','/rooms')
ci = date.today()+timedelta(days=2); co = ci+timedelta(days=2)
room_id = find_available_room(ci, co)
print('room_id',room_id)
booking_payload = {'guest_id':gid,'check_in_date':ci.isoformat(),'check_out_date':co.isoformat(),'room_ids':[room_id]}
code, br = req('POST','/api/bookings',booking_payload)
print('create booking',code,br)
booking_id = br.get('booking_id')
# get invoice
code, inv = req('GET',f'/bookings/{booking_id}/invoice')
print('invoice before payment',code,inv)
# pay full
amount = inv['balance']
code, pay = req('POST',f'/bookings/{booking_id}/payments',{'amount':amount,'payment_method':'card'})
print('pay full',code,pay)
if code not in (200,201):
    print('Payment failed, continuing to next scenario')
code, inv2 = req('GET',f'/bookings/{booking_id}/invoice')
print('invoice after payment',code,inv2)

# Scenario 2: Add service and verify invoice
print('\n=== Scenario 2: Add service and verify invoice ===')
# create guest
guest2 = {'full_name':'S2 Guest','email':f's2+{date.today().isoformat()}@example.com','phone':'0987654321'}
code,res = req('POST','/api/guests',guest2)
g2 = res.get('id')
ci = date.today()+timedelta(days=3); co = ci+timedelta(days=1)
room_id = find_available_room(ci, co)
booking_payload = {'guest_id':g2,'check_in_date':ci.isoformat(),'check_out_date':co.isoformat(),'room_ids':[room_id]}
code, br = req('POST','/api/bookings',booking_payload)
print('create booking',code,br)
booking_id2 = br.get('booking_id')
booking_detail_id = br['details'][0]['booking_detail_id']
# pick service and employee
code, services = req('GET','/services')
svc = None
if code == 200 and services:
    svc = services['items'][0] if isinstance(services,dict) and 'items' in services else (services[0] if services else None)
    s_id = svc.get('service_id') if svc else None
code, emps = req('GET','/employees')
emp = None
if code == 200 and emps:
    items = emps.get('items') if isinstance(emps, dict) and 'items' in emps else (emps if isinstance(emps, list) else [])
    if items:
        emp = items[0]
e_id = None
if emp:
    e_id = emp.get('employee_id') or emp.get('id')
# fallback to first seeded employee id if none found
if not e_id:
    try:
        e_id = 1
    except Exception:
        e_id = None
svc_id = s_id; emp_id = e_id
print('svc_id,emp_id',svc_id,emp_id)
# add service
# add service
code, addsvc = req('POST',f'/booking-details/{booking_detail_id}/services',{'service_id':svc_id,'employee_id':emp_id,'quantity':2})
print('add service',code,addsvc)
if code not in (200,201):
    print('Could not add service, continuing')
# invoice after
code, inv3 = req('GET',f'/bookings/{booking_id2}/invoice')
print('invoice after service',code,inv3)

# Scenario 3: Cancel booking and verify availability
print('\n=== Scenario 3: Cancel booking and verify room availability ===')
# create guest
guest3 = {'full_name':'S3 Guest','email':f's3+{date.today().isoformat()}@example.com','phone':'011223344'}
code,res = req('POST','/api/guests',guest3)
g3 = res.get('id')
ci = date.today()+timedelta(days=10); co = ci+timedelta(days=2)
room_id = find_available_room(ci, co)
booking_payload = {'guest_id':g3,'check_in_date':ci.isoformat(),'check_out_date':co.isoformat(),'room_ids':[room_id]}
code, br = req('POST','/api/bookings',booking_payload)
print('create booking',code,br)
booking_id3 = br.get('booking_id')
# check rooms unavailable for that date
code, available_before = req('GET',f'/rooms?check_in_date={ci.isoformat()}&check_out_date={co.isoformat()}')
print('rooms for dates before cancel',code,available_before)
# cancel booking
code, cancelr = req('PUT',f'/api/bookings/{booking_id3}/status?status_name=cancelled')
print('cancel booking',code,cancelr)
# check rooms available after cancel
code, available_after = req('GET',f'/rooms?check_in_date={ci.isoformat()}&check_out_date={co.isoformat()}')
print('rooms for dates after cancel',code,available_after)

print('\nExtended E2E scenarios completed')
