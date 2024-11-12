from .base_intent_handler import BaseIntentHandler
from ...utils.constants import GET_ACTIVE_USERS_COUNT_INTENT

class GetActiveUsersCountIntentHandler(BaseIntentHandler):
    INTENT_NAME = GET_ACTIVE_USERS_COUNT_INTENT

    def can_handle(self, intent_name):
        """
        Determines if intent passed to class matches the handler
        """
        return intent_name == self.INTENT_NAME
    
    def handle_intent(self, parameters, auth0_service):
        endpoint = f'stats/active-users'

        response_data = auth0_service.get(endpoint)

        needs_file_upload = False

        formatted_response = self.format_response(response_data)

        return formatted_response, needs_file_upload

    def format_response(self, res):
        return f"Found {str(res)} monthly active users on your tenant."