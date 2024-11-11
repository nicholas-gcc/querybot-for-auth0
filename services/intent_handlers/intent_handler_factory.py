from .get_user_by_id_handler import GetUserByIdIntentHandler
from .search_user_by_email_handler import SearchUsersByEmailIntent

class IntentHandlerFactory:
    def __init__(self):
        self.handlers = [
            GetUserByIdIntentHandler(),
            SearchUsersByEmailIntent()
        ]
    
    def get_handler(self, intent_name):
        for handler in self.handlers:
            if handler.can_handle(intent_name):
                return handler
        return None  # No handler found for the intent