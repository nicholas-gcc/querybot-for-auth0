import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import requests

from ...services.auth0_service import Auth0Service
from ...dao.m2m_credentials_dao import m2m_credentials_dao
from ..testutils.constants import (
    AUTH0_API_AUDIENCE_TEMPLATE,
    AUTH0_API_BASE_URL_TEMPLATE,
    AUTH0_TOKEN_URL_TEMPLATE,
    AUTHORIZATION_HEADER_TEMPLATE,
)

class TestAuth0Service(unittest.TestCase):

    def setUp(self):
        self.auth0_base_url = 'your-domain.auth0.com'
        self.client_id = 'test_client_id'
        self.client_secret = 'test_client_secret'
        self.slack_user_id = 'U12345678'
        self.access_token = None
        self.token_expires_at = None

        self.auth0_service = Auth0Service(
            auth0_base_url=self.auth0_base_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            slack_user_id=self.slack_user_id,
            access_token=self.access_token,
            token_expires_at=self.token_expires_at
        )

    @patch('...services.auth0_service.requests.post')
    @patch('...services.auth0_service.m2m_credentials_dao')
    def test_request_new_access_token_success(self, mock_m2m_credentials_dao, mock_requests_post):
        # Mock the response from Auth0 token endpoint
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        # Call the method under test
        token_data = self.auth0_service.request_new_access_token()

        # Assertions
        self.assertEqual(token_data['access_token'], 'new_access_token')
        self.assertEqual(self.auth0_service.access_token, 'new_access_token')
        self.assertIsNotNone(self.auth0_service.token_expires_at)

        # Ensure that the access token and expiry were updated in the DAO
        mock_m2m_credentials_dao.update_access_token.assert_called_once()

    @patch('...services.auth0_service.Auth0Service.get_access_token')
    @patch('...services.auth0_service.requests.get')
    def test_get_success(self, mock_requests_get, mock_get_access_token):
        # Mock the access token retrieval
        mock_get_access_token.return_value = 'valid_access_token'

        # Mock the GET request response
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # Call the method under test
        endpoint = 'users'
        response = self.auth0_service.get(endpoint)

        # Assertions
        self.assertEqual(response, {'data': 'test_data'})
        mock_get_access_token.assert_called_once()
        mock_requests_get.assert_called_once()

    @patch('...services.auth0_service.requests.post')
    def test_request_new_access_token_failure(self, mock_requests_post):
        # Simulate a failed token request
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error")
        mock_requests_post.return_value = mock_response

        # Call the method under test and expect an exception
        with self.assertRaises(Exception):
            self.auth0_service.request_new_access_token()

    @patch('...services.auth0_service.Auth0Service.request_new_access_token')
    def test_get_access_token_uses_cached_token(self, mock_request_new_token):
        # Set a valid cached token
        self.auth0_service.access_token = 'cached_access_token'
        self.auth0_service.token_expires_at = (datetime.utcnow() + timedelta(minutes=5)).isoformat()

        # Call the method under test
        token = self.auth0_service.get_access_token()

        # Assertions
        self.assertEqual(token, 'cached_access_token')
        mock_request_new_token.assert_not_called()

    @patch('...services.auth0_service.Auth0Service.request_new_access_token')
    def test_get_access_token_refreshes_expired_token(self, mock_request_new_token):
        # Set an expired token
        self.auth0_service.access_token = 'expired_access_token'
        self.auth0_service.token_expires_at = (datetime.utcnow() - timedelta(minutes=5)).isoformat()

        # Mock the token refresh method
        mock_request_new_token.return_value = {'access_token': 'new_access_token'}

        # Call the method under test
        token = self.auth0_service.get_access_token()

        # Assertions
        self.assertEqual(token, 'new_access_token')
        mock_request_new_token.assert_called_once()

    @patch('...services.auth0_service.Auth0Service.get_access_token')
    @patch('...services.auth0_service.requests.get')
    def test_get_http_error(self, mock_requests_get, mock_get_access_token):
        # Mock the access token retrieval
        mock_get_access_token.return_value = 'valid_access_token'

        # Simulate an HTTP error during GET request
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_requests_get.return_value = mock_response

        # Call the method under test and expect an exception
        with self.assertRaises(Exception):
            self.auth0_service.get('invalid/endpoint')

    @patch('...services.auth0_service.Auth0Service.get_access_token')
    @patch('...services.auth0_service.requests.get')
    def test_get_unexpected_error(self, mock_requests_get, mock_get_access_token):
        # Mock the access token retrieval
        mock_get_access_token.return_value = 'valid_access_token'

        # Simulate an unexpected error during GET request
        mock_requests_get.side_effect = Exception("Unexpected Error")

        # Call the method under test and expect an exception
        with self.assertRaises(Exception):
            self.auth0_service.get('users')
