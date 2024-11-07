import requests
import jwt
import time

class Auth0Service:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Auth0Service, cls).__new__(cls)
        return cls._instance

    def __init__(self, base_url, client_id, client_secret):
        if not hasattr(self, "initialized"):
            self.base_url = base_url
            self.client_id = client_id
            self.client_secret = client_secret
            self.access_token = None
            self.initialized = True
    
    def get_management_api_token(self):
        if self.access_token and not self.is_token_expired(self.access_token):
            return self.access_token
        else:
            # Token is expired or doesn't exist; request a new one
            url = f"https://{self.base_url}/oauth/token"
            payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": f"https://{self.base_url}/api/v2/",
                "grant_type": "client_credentials"
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Will raise an exception for 4xx/5xx responses
            
            self.access_token = response.json()["access_token"]
            return self.access_token
        


    def is_token_expired(self, token):
        try:
            # Decode the token without verification to extract the payload
            # Set options={'verify_signature': False} to skip signature verification
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            # Extract the 'exp' claim
            exp_timestamp = unverified_payload.get('exp')
            if exp_timestamp is None:
                return True
            
            # Get the current UNIX timestamp
            current_timestamp = int(time.time())

            return current_timestamp >= exp_timestamp

        except jwt.DecodeError:
            return True
        except Exception as e:
            return True