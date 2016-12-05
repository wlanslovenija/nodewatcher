import base64
import hashlib
import hmac
import json
import requests

body = {
    'sensors.generic': {
        '_meta': {'version': 1},
        'foo': {'name': 'Foo Sensor', 'unit': 'F', 'value': 2.0}
    }
}

body = json.dumps(body)
signature = base64.b64encode(hmac.new('examplekey', body, hashlib.sha256).digest())
response = requests.post(
    'http://localhost:8000/push/http/bae00f00-877e-41fc-95a5-d45faf8d77e7',
    data=body,
    headers={
        'X-Nodewatcher-Signature-Algorithm': 'hmac-sha256',
        'X-Nodewatcher-Signature': signature,
    }
)
print(response)
