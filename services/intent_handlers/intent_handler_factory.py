from .get_user_by_id_handler import GetUserByIdIntentHandler
from .search_user_by_email_handler import SearchUsersByEmailIntentHandler
from .get_active_users_count_intent_handler import GetActiveUsersCountIntentHandler
from .get_tenant_settings_intent_handler import GetTenantSettingsIntentHandler
from .get_stats_intent_handler import GetStatsIntentHandler
from .get_ulp_template_intent_handler import GetULPTemplateIntentHandler

class IntentHandlerFactory:
    def __init__(self):
        self.handlers = [
            GetUserByIdIntentHandler(),
            SearchUsersByEmailIntentHandler(),
            GetActiveUsersCountIntentHandler(),
            GetTenantSettingsIntentHandler(),
            GetStatsIntentHandler(),
            GetULPTemplateIntentHandler()
        ]
    
    def get_handler(self, intent_name):
        """
        Matches handler to intent, instantiates the handler based on intent
        """
        for handler in self.handlers:
            if handler.can_handle(intent_name):
                return handler
        return None  # No handler found for the intent