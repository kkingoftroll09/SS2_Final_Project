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

print('Starting E2E test against', BASE)

# 1) Create guest
guest_payload = {
    'full_name': 'E2E Test Guest',
    'email': f'e2e+{int(date.today().strftime("%Y%m%d"))}@example.com',
    'phone': '0123456789',
    'address': '123 Test St'
}
code, res = req('POST', '/api/guests', guest_payload)
print('Create guest:', code, res)
if not res or (code not in (200,201)):
    print('Failed to create guest; aborting')
    raise SystemExit(1)
guest_id = res.get('id') or res.get('guest_id')

# 2) Find an available room
code, rooms = req('GET', '/rooms')
print('Rooms list:', code)
if rooms and isinstance(rooms, dict) and 'items' in rooms:
    room_items = rooms['items']
else:
    room_items = rooms if isinstance(rooms, list) else []

room_id = None
for r in room_items:
    # r may contain id or room_id
    if r.get('status') == 'available' or r.get('status') is None:
        room_id = r.get('id') or r.get('room_id') or r.get('room_id')
        if room_id:
            break

if not room_id:
    print('No available room found; aborting')
    raise SystemExit(2)
print('Using room id', room_id)

# 3) Create booking for tomorrow
ci = date.today() + timedelta(days=1)
co = ci + timedelta(days=1)
booking_payload = {
    'guest_id': guest_id,
    'check_in_date': ci.isoformat(),
    'check_out_date': co.isoformat(),
    'room_ids': [room_id]
}
code, br = req('POST', '/api/bookings', booking_payload)
print('Create booking:', code, br)
if not br or code not in (200,201):
    print('Failed to create booking; aborting')
    raise SystemExit(3)
booking_id = br.get('booking_id') or br.get('id')

# 4) Add payment for booking
payment_payload = {'amount': 50.0, 'payment_method': 'cash'}
code, pr = req('POST', f'/bookings/{booking_id}/payments', payment_payload)
print('Add payment:', code, pr)
if code not in (200,201):
    print('Failed to add payment; aborting')
    raise SystemExit(4)

# 5) Get payments for booking
code, payments = req('GET', f'/bookings/{booking_id}/payments')
print('Payments for booking:', code, payments)

# 6) Get invoice
code, invoice = req('GET', f'/bookings/{booking_id}/invoice')
print('Invoice:', code, invoice)

# 7) Verify payments appear in global payments list
code, allp = req('GET', '/payments')
print('All payments:', code, (len(allp) if isinstance(allp, list) else allp))

print('E2E test completed')
