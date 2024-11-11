import json
from .base_intent_handler import BaseIntentHandler
from ...utils.constants import MULTILINE_CODE_DELIMITER, GET_USER_BY_ID_INTENT, USER_ID_PARAM, MAX_MESSAGE_LENGTH, NO_DATA_MESSAGE

class GetUserByIdIntentHandler(BaseIntentHandler):
    INTENT_NAME = GET_USER_BY_ID_INTENT

    def can_handle(self, intent_name):
        return intent_name == self.INTENT_NAME

    def handle_intent(self, parameters, auth0_service):
        user_id = parameters[USER_ID_PARAM]
        endpoint = f'users/{user_id}'

        response_data = auth0_service.get(endpoint)
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
        formatted_json = json.dumps(res, indent=4)
        return formatted_json