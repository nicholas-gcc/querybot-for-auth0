import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from pymongo.collection import Collection

from ..db.mongo_client import mongo_client
from ..utils.constants import M2M_CREDENTIALS_COLLECTION

logger = logging.getLogger(__name__)


class M2MCredentialsDAO:
    """
    Data Access Object for managing machine-to-machine credentials in MongoDB.
    """

    def __init__(self):
        """
        Initialize the DAO with the MongoDB collection.
        """
        try:
            self.collection: Collection = mongo_client.get_collection(
                M2M_CREDENTIALS_COLLECTION
            )
            logger.info(f"Connected to collection: {M2M_CREDENTIALS_COLLECTION}")
        except Exception as e:
            logger.exception("Failed to connect to MongoDB collection.")
            raise

    def get_credentials(self, slack_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve credentials for a given Slack user ID.

        Args:
            slack_user_id (str): The Slack user ID.

        Returns:
            Optional[Dict[str, Any]]: The credentials document or None if not found.
        """
        if not slack_user_id:
            logger.error("Slack user ID must be provided.")
            raise ValueError("Slack user ID must be provided.")

        try:
            credentials = self.collection.find_one({"slack_user_id": slack_user_id})
            logger.debug(f"Retrieved credentials for user {slack_user_id}: {credentials}")
            return credentials
        except Exception as e:
            logger.exception(f"Error retrieving credentials for user {slack_user_id}.")
            raise

    def upsert_credentials(
        self, slack_user_id: str, credentials: Dict[str, Any]
    ) -> None:
        """
        Insert or update credentials for a given Slack user ID.

        Args:
            slack_user_id (str): The Slack user ID.
            credentials (Dict[str, Any]): The credentials data to upsert.
        """
        if not slack_user_id or not credentials:
            logger.error("Slack user ID and credentials must be provided.")
            raise ValueError("Slack user ID and credentials must be provided.")

        try:
            credentials['slack_user_id'] = slack_user_id
            result = self.collection.update_one(
                {"slack_user_id": slack_user_id},
                {"$set": credentials},
                upsert=True
            )
            logger.debug(f"Upserted credentials for user {slack_user_id}. Result: {result.raw_result}")
        except Exception as e:
            logger.exception(f"Error upserting credentials for user {slack_user_id}.")
            raise

    def update_access_token(
        self, slack_user_id: str, access_token: str, expires_in: int
    ) -> None:
        """
        Update the access token and expiry time for a given Slack user ID.

        Args:
            slack_user_id (str): The Slack user ID.
            access_token (str): The new access token.
            expires_in (int): The number of seconds until the token expires.
        """
        if not slack_user_id or not access_token or expires_in is None:
            logger.error("Slack user ID, access token, and expires_in must be provided.")
            raise ValueError("Slack user ID, access token, and expires_in must be provided.")

        try:
            token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            result = self.collection.update_one(
                {"slack_user_id": slack_user_id},
                {
                    "$set": {
                        "access_token": access_token,
                        "token_expires_at": token_expires_at.isoformat(),
                    }
                }
            )
            logger.debug(f"Updated access token for user {slack_user_id}. Result: {result.raw_result}")
        except Exception as e:
            logger.exception(f"Error updating access token for user {slack_user_id}.")
            raise


m2m_credentials_dao = M2MCredentialsDAO()
