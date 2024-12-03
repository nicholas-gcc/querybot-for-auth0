import json
import logging
from typing import Any, Dict, Tuple

from .base_intent_handler import BaseIntentHandler
from ...utils.constants import (
    GET_USER_BY_ID_INTENT,
    MAX_MESSAGE_LENGTH,
    MULTILINE_CODE_DELIMITER,
    NO_DATA_MESSAGE,
    USER_ID_PARAM,
)

logger = logging.getLogger(__name__)


class GetUserByIdIntentHandler(BaseIntentHandler):
    """
    Intent handler for retrieving a user by ID.
    """

    INTENT_NAME = GET_USER_BY_ID_INTENT

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
        Liaises with the Auth0 Management API to get user information by ID.

        Args:
            parameters (Dict[str, Any]): Parameters extracted from the user's message.
            auth0_service: The Auth0 service instance for making API calls.

        Returns:
            Tuple[str, bool, None]: A tuple containing the formatted response,
            a flag indicating if file upload is needed,
            and additional text (None).
        """
        user_id = parameters.get(USER_ID_PARAM)
        if not user_id:
            logger.error("User ID parameter is missing.")
            return "User ID is required to retrieve user information.", False, None

        endpoint = f'users/{user_id}'

        try:
            logger.debug(f"Requesting user information from {endpoint}")
            response_data = auth0_service.get(endpoint)

            if not response_data:
                logger.info(f"No data received for user ID {user_id}.")
                return NO_DATA_MESSAGE, False, None

            formatted_response = self.format_response(response_data)

            # Check if the formatted response exceeds Slack's limit
            if len(formatted_response) > MAX_MESSAGE_LENGTH:
                needs_file_upload = True
            else:
                needs_file_upload = False
                formatted_response = (
                    f"{MULTILINE_CODE_DELIMITER}{formatted_response}{MULTILINE_CODE_DELIMITER}"
                )

            return formatted_response, needs_file_upload, None

        except Exception as e:
            logger.exception("Error handling GetUserById intent.")
            return f"An error occurred: {str(e)}", False, None

    def format_response(self, res: Any) -> str:
        """
        Pretty print JSON response from Auth0.

        Args:
            res (Any): The response data from the API.

        Returns:
            str: The formatted JSON string.
        """
        formatted_json = json.dumps(res, indent=4)
        return formatted_json
