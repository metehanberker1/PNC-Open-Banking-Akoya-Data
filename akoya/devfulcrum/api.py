import json
import base64
import requests
import threading
from datetime import datetime

class AkoyaClient:

    def __init__(self, app_key, app_secret, callback_url="https://127.0.0.1", tokens_file="tokens.json", timeout=5, verbose=True):
        """
        Initialize a client to access the Akoya API.
        :param app_key: app key credentials
        :type app_key: str
        :param app_secret: app secret credentials
        :type app_secret: str
        :param callback_url: URL for callback
        :type callback_url: str
        :param tokens_file: path to tokens file
        :type tokens_file: str
        :param timeout: request timeout
        :type timeout: int
        :param verbose: print extra information
        :type verbose: bool
        """

        if app_key is None or app_secret is None or callback_url is None or tokens_file is None:
            raise ValueError("app_key, app_secret, callback_url, and tokens_file cannot be None.")

        self._app_key = app_key
        self._app_secret = app_secret
        self._callback_url = callback_url
        self.access_token = None
        self.refresh_token = None
        self._access_token_issued = None    # datetime of access token issue
        self._refresh_token_issued = None   # datetime of refresh token issue
        self._access_token_timeout = 1800   # in seconds (default assumption)
        self._refresh_token_timeout = 7     # in days (default assumption)
        self._tokens_file = tokens_file     # path to tokens file
        self.timeout = timeout
        self._verbose = verbose             # verbose mode

        # Try to load tokens from the tokens file
        at_issued, rt_issued, token_dictionary = self._read_tokens_file()
        if None not in [at_issued, rt_issued, token_dictionary]:
            self.access_token = token_dictionary.get("access_token")
            self.refresh_token = token_dictionary.get("refresh_token")
            self._access_token_issued = at_issued
            self._refresh_token_issued = rt_issued
            self.update_tokens()
        else:
            open(self._tokens_file, 'w').close()
            self._update_refresh_token()

        if self._verbose:
            print("Initialization Complete")

    def update_tokens(self):
        """
        Checks if tokens need to be updated and updates if needed.
        """
        if (datetime.now() - self._refresh_token_issued).days >= (self._refresh_token_timeout - 1):
            print("The refresh token has expired, please update!")
            self._update_refresh_token()
        elif (datetime.now() - self._access_token_issued).seconds > (self._access_token_timeout - 60):
            if self._verbose:
                print("The access token has expired, updating automatically.")
            self._update_access_token()

    def update_tokens_auto(self):
        """
        Spawns a thread to check and update the access token periodically.
        """
        def checker():
            import time
            while True:
                self.update_tokens()
                time.sleep(60)

        threading.Thread(target=checker, daemon=True).start()

    def _update_access_token(self):
        """
        Refresh the access token using the refresh token.
        """
        at_issued, rt_issued, token_dictionary = self._read_tokens_file()
        response = self._post_oauth_token('refresh_token', token_dictionary.get("refresh_token"))
        if response.ok:
            self._access_token_issued = datetime.now()
            new_tokens = response.json()
            self.access_token = new_tokens.get("access_token")
            self.refresh_token = new_tokens.get("refresh_token")
            self._write_tokens_file(self._access_token_issued, rt_issued, new_tokens)
            if self._verbose:
                print(f"Access token updated: {self._access_token_issued}")
        else:
            print("Failed to update access token.")

    def _update_refresh_token(self):
        """
        Get new access and refresh tokens using authorization code.
        """
        import webbrowser
        print("Please authorize this program to access your Akoya account.")
        auth_url = f'https://sandbox-idp.ddp.akoya.com/auth?connector=mikomo&client_id={self._app_key}&redirect_uri=https://recipient.ddp.akoya.com/flow/callback&response_type=code&scope=openid%20offline_access&state=appstate'
        # auth_url = f'https://sandbox-idp.ddp.akoya.com/auth?connector=mikomo&client_id={self._app_key}&redirect_uri={self._callback_url}&response_type=code&scope=openid%20offline_access&state=appstate'
        print(f"Click to authenticate: {auth_url}")
        webbrowser.open(auth_url)
        response_url = input("Paste the full redirected URL here: ")
        code = self._extract_authorization_code(response_url)
        response = self._post_oauth_token('authorization_code', code)
        if response.ok:
            self._access_token_issued = self._refresh_token_issued = datetime.now()
            new_tokens = response.json()
            self.access_token = new_tokens.get("access_token")
            self.refresh_token = new_tokens.get("refresh_token")
            self._write_tokens_file(self._access_token_issued, self._refresh_token_issued, new_tokens)
            print("Tokens updated successfully.")
        else:
            print("Failed to update tokens. Ensure your app credentials and authorization code are correct.")

    def _post_oauth_token(self, grant_type, code):
        """
        Makes API calls for OAuth token management.
        """
        headers = {
            'Authorization': f'Basic {base64.b64encode(bytes(f"{self._app_key}:{self._app_secret}", "utf-8")).decode("utf-8")}',
            'Content-Type': 'application/x-www-form-urlencoded'}
        if grant_type == 'authorization_code':
            data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': self._callback_url}
        elif grant_type == 'refresh_token':
            data = {'grant_type': 'refresh_token', 'refresh_token': code}
        else:
            print("Invalid grant type")
            return None
        return requests.post('https://api.akoya.com/oauth/token', headers=headers, data=data)

    def _extract_authorization_code(self, url):
        """
        Extract the authorization code from the URL.
        """
        import urllib.parse
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        return query_params.get('code', [None])[0]

    def _write_tokens_file(self, at_issued, rt_issued, token_dictionary):
        """
        Writes token file.
        """
        try:
            with open(self._tokens_file, 'w') as f:
                to_write = {
                    "access_token_issued": at_issued.isoformat(),
                    "refresh_token_issued": rt_issued.isoformat(),
                    "token_dictionary": token_dictionary
                }
                json.dump(to_write, f, indent=4)
        except Exception as e:
            print(f"Error writing token file: {e}")

    def _read_tokens_file(self):
        """
        Reads token file.
        """
        try:
            with open(self._tokens_file, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get("access_token_issued")), datetime.fromisoformat(data.get("refresh_token_issued")), data.get("token_dictionary")
        except Exception:
            return None, None, None
