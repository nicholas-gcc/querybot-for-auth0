import json
import logging
from typing import Any, Dict, Tuple

from .base_intent_handler import BaseIntentHandler
from ...utils.constants import (
    GET_TENANT_SETTINGS_INTENT,
    MAX_MESSAGE_LENGTH,
    MULTILINE_CODE_DELIMITER,
    NO_DATA_MESSAGE,
)

logger = logging.getLogger(__name__)


class GetTenantSettingsIntentHandler(BaseIntentHandler):
    """
    Intent handler for retrieving tenant settings.
    """

    INTENT_NAME = GET_TENANT_SETTINGS_INTENT

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
        Liaises with the Auth0 Management API to get tenant settings and formats the response.

        Args:
            parameters (Dict[str, Any]): Parameters extracted from the user's message.
            auth0_service: The Auth0 service instance for making API calls.

        Returns:
            Tuple[str, bool, None]: A tuple containing the formatted response,
            a flag indicating if file upload is needed,
            and additional text (None).
        """
        endpoint = 'tenants/settings'

        try:
            logger.debug(f"Requesting tenant settings from {endpoint}")
            response_data = auth0_service.get(endpoint)

            if not response_data:
                logger.info("No data received for tenant settings.")
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
            logger.exception("Error handling GetTenantSettings intent.")
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
