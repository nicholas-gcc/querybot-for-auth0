import requests
import jwt
import time

from threading import Lock, Thread

class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton. 
    Credits: https://refactoring.guru/design-patterns/singleton/python/example#example-1
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class Auth0Service(metaclass=SingletonMeta):
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
    
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