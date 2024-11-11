from abc import ABC, abstractmethod

class BaseIntentHandler(ABC):

    @abstractmethod
    def can_handle(self, intent_name):
        pass

    @abstractmethod
    def handle_intent(self, parameters, auth0_service):
        pass

    @abstractmethod
    def format_response(res):
        pass