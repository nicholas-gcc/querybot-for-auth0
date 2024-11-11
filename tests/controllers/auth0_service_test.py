import unittest
import jwt
import time
import uuid
from ...services.auth0_service import Auth0Service
from ..testutils.constants import AUTH0_BASE_URL, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET

class TestAuth0Service(unittest.TestCase):

    def setUp(self):
        self.auth0_service = Auth0Service(AUTH0_BASE_URL, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET)

    def test_singleton(self):
        new_auth0_service = Auth0Service(AUTH0_BASE_URL, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET)
        self.assertTrue(self.auth0_service is new_auth0_service)
        self.assertEqual(self.auth0_service.get_management_api_token(), new_auth0_service.get_management_api_token())

    def test_getManagementApiToken_returnsValidToken(self):
        try:
            token = self.auth0_service.get_management_api_token()
            jwt.decode(token, options={"verify_signature": False})
            self.assertTrue(True, "Decoding should not raise an error.")
        except jwt.DecodeError:
            self.fail("DecodeError was raised when decoding a valid token.")
        except Exception as e:
            self.fail(f"An unexpected exception was raised: {e}")

    def test_isTokenExpired_unexpiredToken(self):
        payload = {
            'exp': int(time.time()) + 300  # expires in 5 minutes
        }
        testing_secret_key = str(uuid.uuid4())
        token = jwt.encode(payload, testing_secret_key, algorithm='HS256')
        self.assertFalse(self.auth0_service.is_token_expired(token), "Token should be valid, but it was detected as expired.")

    def test_isTokenExpired_expiredToken(self):
        payload = {
            'exp': int(time.time()) - 300  # expires in 5 minutes
        }
        testing_secret_key = str(uuid.uuid4())
        token = jwt.encode(payload, testing_secret_key, algorithm='HS256')
        self.assertTrue(self.auth0_service.is_token_expired(token), "Token should be expired, but it was detected as valid.")

    def test_isTokenExpired_withoutExpClaim(self):
        payload = {
            'data': 'some_value'
        }
        testing_secret_key = str(uuid.uuid4())
        token = jwt.encode(payload, testing_secret_key, algorithm='HS256')
        self.assertTrue(self.auth0_service.is_token_expired(token), "Token without 'exp' claim should be considered expired")

    def test_isTokenExpired_malformedToken(self):
        malformed_token = '123'
        self.assertTrue(self.auth0_service.is_token_expired(malformed_token), "Malformed token should be considered expired")