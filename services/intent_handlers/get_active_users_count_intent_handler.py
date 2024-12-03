import logging
from typing import Any, Dict, Tuple

from .base_intent_handler import BaseIntentHandler
from ...utils.constants import (
    GET_ACTIVE_USERS_COUNT_INTENT,
    NO_DATA_MESSAGE,
)

logger = logging.getLogger(__name__)


class GetActiveUsersCountIntentHandler(BaseIntentHandler):
    """
    Intent handler for retrieving the count of active users.
    """

    INTENT_NAME = GET_ACTIVE_USERS_COUNT_INTENT

    def can_handle(self, intent_name: str) -> bool:
        """
        Determines if this handler can handle the given intent.

        Args:
            intent_name (str): The name of the intent.

        Returns:
            bool: True if it can handle the intent, False otherwise.
        """
        return intent_name == self.INTENT_NAME

    def handle_intent(
        self, parameters: Dict[str, Any], auth0_service
    ) -> Tuple[str, bool, None]:
        """
        Handles the intent to get the count of active users.

        Args:
            parameters (Dict[str, Any]): Parameters extracted from the user's message.
            auth0_service: The Auth0 service instance for making API calls.

        Returns:
            Tuple[str, bool, None]: A tuple containing the formatted response,
            a flag indicating if file upload is needed (always False here),
            and additional text (None).
        """
        endpoint = 'stats/active-users'
        try:
            logger.debug(f"Requesting active users count from {endpoint}")
            response_data = auth0_service.get(endpoint)

            if not response_data:
                logger.info("No data received for active users count.")
                return NO_DATA_MESSAGE, False, None

            formatted_response = self.format_response(response_data)

            return formatted_response, False, None

        except Exception as e:
            logger.exception("Error handling GetActiveUsersCount intent.")
            return f"An error occurred: {str(e)}", False, None

    def format_response(self, res: Any) -> str:
        """
        Formats the API response.

        Args:
            res (Any): The response data from the API.

        Returns:
            str: The formatted response string.
        """
        return f"Found {str(res)} monthly active users on your tenant."
