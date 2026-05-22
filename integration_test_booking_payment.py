import urllib.request, urllib.parse, json
from datetime import date, timedelta
import sys

BASE='http://127.0.0.1:8000'


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

# Scenario: create guest, create booking, get invoice, pay full amount
print('Running integration test: booking -> invoice -> payment')
# create guest
guest = {'full_name':'IT Test','email':f'it+{date.today().isoformat()}@example.com','phone':'000000000'}
code,res = req('POST','/api/guests',guest)
if code not in (200,201):
    print('Failed to create guest',code,res); sys.exit(2)

gid = res.get('id')
ci = date.today()+timedelta(days=2); co = ci+timedelta(days=1)
# find a room
code, rooms = req('GET', f'/rooms?check_in_date={ci.isoformat()}&check_out_date={co.isoformat()}')
if code != 200:
    print('Failed to list rooms',code,rooms); sys.exit(2)
items = rooms.get('items') if isinstance(rooms, dict) and 'items' in rooms else rooms
if not items:
    print('No rooms available'); sys.exit(2)
room_id = items[0].get('id') or items[0].get('room_id')
booking_payload = {'guest_id':gid,'check_in_date':ci.isoformat(),'check_out_date':co.isoformat(),'room_ids':[room_id]}
code, br = req('POST','/api/bookings',booking_payload)
if code not in (200,201):
    print('Booking creation failed',code,br); sys.exit(2)
booking_id = br.get('booking_id')
# invoice
code, inv = req('GET', f'/bookings/{booking_id}/invoice')
if code != 200:
    print('Invoice failed',code,inv); sys.exit(2)
amount = inv.get('balance')
code, pay = req('POST', f'/bookings/{booking_id}/payments', {'amount': amount, 'payment_method':'card'})
if code not in (200,201):
    print('Payment failed',code,pay); sys.exit(2)
print('Integration test passed')
sys.exit(0)
