from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple


class BaseIntentHandler(ABC):
    """
    Abstract base class for intent handlers.
    """

    @abstractmethod
    def can_handle(self, intent_name: str) -> bool:
        """
        Determine if the handler can handle the given intent.

        Args:
            intent_name (str): The name of the intent.

        Returns:
            bool: True if the handler can handle the intent, False otherwise.
        """
        pass

    @abstractmethod
    def handle_intent(
        self, parameters: Dict[str, Any], auth0_service
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Handle the intent with the provided parameters and Auth0 service.

        Args:
            parameters (Dict[str, Any]): The parameters extracted from the user's message.
            auth0_service: The Auth0 service instance for making API calls.

        Returns:
            Tuple[str, bool, Optional[str]]: A tuple containing the response,
            a flag indicating if file upload is needed, and any additional text.
        """
        pass

    @abstractmethod
    def format_response(self, res: Any) -> str:
        """
        Format the API response for presentation to the user.

        Args:
            res (Any): The response data from the API.

        Returns:
            str: The formatted response string.
        """
        pass
