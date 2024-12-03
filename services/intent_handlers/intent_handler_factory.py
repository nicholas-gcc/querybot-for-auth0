from typing import Optional

from .get_active_users_count_intent_handler import GetActiveUsersCountIntentHandler
from .get_stats_intent_handler import GetStatsIntentHandler
from .get_tenant_settings_intent_handler import GetTenantSettingsIntentHandler
from .get_ulp_template_intent_handler import GetULPTemplateIntentHandler
from .get_user_by_id_handler import GetUserByIdIntentHandler
from .search_user_by_email_handler import SearchUsersByEmailIntentHandler

from .base_intent_handler import BaseIntentHandler


class IntentHandlerFactory:
    """
    Factory class to instantiate the appropriate intent handler based on the intent name.
    """

    def __init__(self):
        """
        Initialize the IntentHandlerFactory with all available handlers.
        """
        self.handlers = [
            GetUserByIdIntentHandler(),
            SearchUsersByEmailIntentHandler(),
            GetActiveUsersCountIntentHandler(),
            GetTenantSettingsIntentHandler(),
            GetStatsIntentHandler(),
            GetULPTemplateIntentHandler(),
        ]

    def get_handler(self, intent_name: str) -> Optional[BaseIntentHandler]:
        """
        Retrieve the handler that can handle the given intent.

        Args:
            intent_name (str): The name of the intent.

        Returns:
            Optional[BaseIntentHandler]: The handler instance if found, else None.
        """
        for handler in self.handlers:
            if handler.can_handle(intent_name):
                return handler
        return None  # No handler found for the intent
