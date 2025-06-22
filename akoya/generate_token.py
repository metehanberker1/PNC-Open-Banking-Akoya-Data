import requests
from requests.auth import HTTPBasicAuth

url = "https://sandbox-idp.ddp.akoya.com/token"

payload = { "grant_type": "authorization_code", "code": "ory_ac_....", "redirect_uri": "https://recipient.ddp.akoya.com/flow/callback" }
headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded"
}

auth = HTTPBasicAuth('024e4a61....', 'nPKt....')

response = requests.post(url, data=payload, headers=headers, auth=auth)

print(response.text)