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
            return e.code, e.read().decode('utf-8')
    except Exception as e:
        print('ERROR:', e)
        return None, None

print('Debug: Payment 500 error')

# Create guest
guest = {'full_name':'Debug Guest','email':f'debug+{date.today().isoformat()}@example.com','phone':'0123456789'}
code, res = req('POST','/api/guests',guest)
print('Guest:', code, res)
gid = res.get('id')

# Get available rooms for a future date
ci = date.today() + timedelta(days=5)
co = ci + timedelta(days=2)
code, rooms = req('GET',f'/rooms?check_in_date={ci.isoformat()}&check_out_date={co.isoformat()}')
print('Rooms:', code)
room_id = rooms['items'][0]['id'] if rooms and 'items' in rooms else None
print('Room ID:', room_id)

# Create booking
payload = {'guest_id': gid, 'check_in_date': ci.isoformat(), 'check_out_date': co.isoformat(), 'room_ids': [room_id]}
code, br = req('POST','/api/bookings', payload)
print('Booking:', code, br)
bid = br['booking_id']

# Get invoice first
code, inv = req('GET', f'/bookings/{bid}/invoice')
print('Invoice:', code, inv)

# Try payment with amount = balance (full pay)
amount = inv['balance']
payment_payload = {'amount': amount, 'payment_method': 'card'}
print(f'Sending payment: booking_id={bid}, amount={amount}')
code, pay = req('POST', f'/bookings/{bid}/payments', payment_payload)
print('Payment response:', code, pay)
