import requests

# Yodlee API credentials
client_id = "7ySPE...."
client_secret = "oISaaw...."
base_url = "https://sandbox.api.yodlee.com/ysl"

# Endpoint for authentication
auth_url = f"{base_url}/auth/token"

# Request headers
headers = {
    "Api-Version": "1.1", "loginName": "sbMem....",
    "Content-Type": "application/x-www-form-urlencoded",
}

# Request payload
payload = f"clientId={client_id}&secret={client_secret}"

try:
    # Sending POST request to get the authentication token
    response = requests.post(auth_url, headers=headers, data=payload)

    # Raise an exception for HTTP errors
    response.raise_for_status()

    # Parse JSON response
    token_data = response.json()
    print("Authentication Successful!")
    print("Token:", token_data.get("token"))

except requests.exceptions.HTTPError as http_err:
    if response.status_code == 401:
        print("Error: Unauthorized. Please check your credentials.")
    else:
        print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")
