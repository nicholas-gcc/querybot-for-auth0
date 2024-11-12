import json
from .base_intent_handler import BaseIntentHandler
from ...utils.constants import MULTILINE_CODE_DELIMITER, SEARCH_USERS_BY_EMAIL_INTENT, EMAIL_PARAM, NO_DATA_MESSAGE, MAX_MESSAGE_LENGTH

class SearchUsersByEmailIntentHandler(BaseIntentHandler):
    INTENT_NAME = SEARCH_USERS_BY_EMAIL_INTENT

    def can_handle(self, intent_name):
        """
        Determines if intent passed to class matches the handler
        """
        return intent_name == self.INTENT_NAME

    def handle_intent(self, parameters, auth0_service):
        """
        Liases with Management API to get a response and formats it, determines if file upload needed
        """
        email = parameters[EMAIL_PARAM]
        endpoint = f'users-by-email'
        query_params = {EMAIL_PARAM: email}

        response_data = auth0_service.get(endpoint, query_params)
        formatted_response = self.format_response(response_data)

        if response_data == {} or response_data == []:
            return NO_DATA_MESSAGE, False

        # Check if the formatted response exceeds Slack's limit
        if len(formatted_response) > MAX_MESSAGE_LENGTH:
            needs_file_upload = True
        else:
            needs_file_upload = False
            formatted_response = f"{MULTILINE_CODE_DELIMITER}{formatted_response}{MULTILINE_CODE_DELIMITER}"

        return formatted_response, needs_file_upload

    def format_response(self, res):
        """
        Pretty print JSON response from Auth0
        """
        formatted_json = json.dumps(res, indent=4)
        return formatted_json

    