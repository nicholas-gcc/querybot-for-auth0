import logging
from datetime import datetime, timedelta

import requests

from ..dao.m2m_credentials_dao import m2m_credentials_dao
from ..utils.constants import (
    AUTH0_API_AUDIENCE_TEMPLATE,
    AUTH0_API_BASE_URL_TEMPLATE,
    AUTH0_TOKEN_URL_TEMPLATE,
    AUTHORIZATION_HEADER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class Auth0Service:
    """Service for interacting with the Auth0 Management API."""

    def __init__(
        self,
        auth0_base_url: str,
        client_id: str,
        client_secret: str,
        slack_user_id: str,
        access_token: str = None,
        token_expires_at: str = None,
    ):
        """
        Initialize the Auth0Service with user-specific credentials.

        Args:
            auth0_base_url (str): The base URL of the Auth0 tenant (e.g., 'your-domain.auth0.com').
            client_id (str): The client ID for Auth0 Machine-to-Machine application.
            client_secret (str): The client secret for Auth0 Machine-to-Machine application.
            slack_user_id (str): The Slack user ID associated with these credentials.
            access_token (str, optional): The current access token. Defaults to None.
            token_expires_at (str, optional): The token expiry time in ISO format. Defaults to None.
        """
        self.auth0_base_url = auth0_base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.slack_user_id = slack_user_id
        self.access_token = access_token
        self.token_expires_at = token_expires_at

    def get_access_token(self) -> str:
        """
        Retrieve a valid access token, refreshing it if necessary.

        Returns:
            str: The valid access token.

        Raises:
            Exception: If unable to retrieve a valid access token.
        """
        try:
            if self.access_token and self.token_expires_at:
                expires_at = datetime.fromisoformat(self.token_expires_at)
                if datetime.utcnow() < expires_at:
                    logger.debug(
                        "Using cached access token for user %s", self.slack_user_id
                    )
                    return self.access_token  # Token is still valid

            # Token is missing or expired; request a new one
            logger.info(
                "Access token expired or missing for user %s. Requesting new token.",
                self.slack_user_id,
            )
            token_data = self.request_new_access_token()
            return token_data["access_token"]
        except Exception as e:
            logger.exception(
                "Failed to get access token for user %s: %s",
                self.slack_user_id,
                str(e),
            )
            raise

    def request_new_access_token(self) -> dict:
        """
        Request a new access token from Auth0 and update the stored token.

        Returns:
            dict: The token data including access token and expiry.

        Raises:
            Exception: If unable to obtain a new access token.
        """
        try:
            url = AUTH0_TOKEN_URL_TEMPLATE.format(
                auth0_base_url=self.auth0_base_url
            )
            audience = AUTH0_API_AUDIENCE_TEMPLATE.format(
                auth0_base_url=self.auth0_base_url
            )
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": audience,
            }
            logger.debug(
                "Requesting new access token from %s for user %s",
                url,
                self.slack_user_id,
            )
            response = requests.post(url, json=payload)
            response.raise_for_status()
            token_data = response.json()
            # Update the access token and expiry
            expires_in = token_data["expires_in"]
            self.access_token = token_data["access_token"]
            self.token_expires_at = (
                datetime.utcnow() + timedelta(seconds=expires_in)
            ).isoformat()

            # Update in MongoDB
            m2m_credentials_dao.update_access_token(
                self.slack_user_id, self.access_token, expires_in
            )

            logger.info(
                "New access token obtained and stored for user %s",
                self.slack_user_id,
            )
            return token_data
        except requests.exceptions.RequestException as e:
            logger.exception(
                "HTTP error occurred while requesting new access token for user %s: %s",
                self.slack_user_id,
                str(e),
            )
            raise
        except Exception as e:
            logger.exception(
                "An error occurred while requesting new access token for user %s: %s",
                self.slack_user_id,
                str(e),
            )
            raise

    def get(self, endpoint: str, query_params: dict = None) -> dict:
        """
        Make a GET request to the Auth0 Management API.

        Args:
            endpoint (str): The API endpoint to call (e.g., 'users', 'tenants/settings').
            query_params (dict, optional): Query parameters for the request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            Exception: If the GET request fails.
        """
        try:
            # Ensure we have a valid access token
            token = self.get_access_token()
            headers = {
                "Authorization": AUTHORIZATION_HEADER_TEMPLATE.format(token=token)
            }
            url = AUTH0_API_BASE_URL_TEMPLATE.format(
                auth0_base_url=self.auth0_base_url, endpoint=endpoint
            )
            logger.debug(
                "Making GET request to %s for user %s", url, self.slack_user_id
            )
            response = requests.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.exception(
                "HTTP error occurred during GET request to %s: %s", url, str(e)
            )
            raise
        except Exception as e:
            logger.exception(
                "An error occurred during GET request to %s: %s", url, str(e)
            )
            raise