from .get_user_by_id_handler import GetUserByIdIntentHandler
from .search_user_by_email_handler import SearchUsersByEmailIntent
from .get_active_users_count_intent import GetActiveUsersCountIntent

class IntentHandlerFactory:
    def __init__(self):
        self.handlers = [
            GetUserByIdIntentHandler(),
            SearchUsersByEmailIntent(),
            GetActiveUsersCountIntent()
        ]
    
    def get_handler(self, intent_name):
        """
        Matches handler to intent, instantiates the handler based on intent
        """
        for handler in self.handlers:
            if handler.can_handle(intent_name):
                return handler
        return None  # No handler found for the intent