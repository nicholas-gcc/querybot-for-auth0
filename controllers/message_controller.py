import uuid
import os
import json

from ..services.dialogflow_service import DialogflowService
from ..services.auth0_service import Auth0Service
from ..services.intent_handlers.intent_handler_factory import IntentHandlerFactory
from ..utils.string_utils import StringUtils
from ..utils.constants import DIALOGFLOW_PROJECT_ID, DIALOGFLOW_LANGUAGE_CODE_EN, NEWLINE_DELIMITER

class MessageController:

    def __init__(self):
        self.dialogflow_service = DialogflowService()
        self.auth0_service = Auth0Service(
            os.getenv("AUTH0_BASE_URL"),
            os.getenv("AUTH0_CLIENT_ID"),
            os.getenv("AUTH0_CLIENT_SECRET"),
        )
        self.intent_handler_factory = IntentHandlerFactory()


    def process_message(self, message):
        # 1. Take message from Slack
        # 2. Send it to Dialogflow service to pick up intent
        # 3. Get the correct intent handler
        # 4. Get intent handler to make Auth0 Management API call
        sanitized_message = StringUtils().remove_format(message)

        # Since we have defined single-turn agents, session can be arbitrary
        dialogflow_session_id = uuid.uuid4()

        detected_intent, fulfillment_text, parameters = self.dialogflow_service.detect_intent_texts(DIALOGFLOW_PROJECT_ID, dialogflow_session_id, sanitized_message, DIALOGFLOW_LANGUAGE_CODE_EN)

        handler = self.intent_handler_factory.get_handler(detected_intent)

        if handler:
            payload, needs_file_upload = handler.handle_intent(parameters, self.auth0_service)
            response = {
                'text': fulfillment_text,
                'payload': payload,
                'needs_file_upload': needs_file_upload
            }
        else:
            # assume fallback intent is reached
            response = {
                'text': fulfillment_text,
                'payload': None,
                'needs_file_upload': False
            }

        return response
        