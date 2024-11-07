import uuid

from ..services.dialogflow_service import DialogflowService
from ..utils.string_utils import StringUtils
from ..utils.constants import DIALOGFLOW_PROJECT_ID, DIALOGFLOW_LANGUAGE_CODE_EN

class MessageController:

    def __init__(self):
        pass

    def process_message(self, message):
        # 1. Take message from Slack
        # 2. Send it to Dialogflow service to pick up intent
        # 3. Get the correct intent handler
        # 4. Get intent handler to make Auth0 Management API call
        sanitized_message = StringUtils().remove_format(message)

        # Since we have defined single-turn agents, session can be arbitrary
        dialogflow_session_id = uuid.uuid4()

        detected_intent, fulfillment_text = DialogflowService().detect_intent_texts(DIALOGFLOW_PROJECT_ID, dialogflow_session_id, sanitized_message, DIALOGFLOW_LANGUAGE_CODE_EN)
        return "Detected intent: " + detected_intent + "\nFulfillment text: " + fulfillment_text