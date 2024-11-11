import unittest
import uuid
from ...services.dialogflow_service import DialogflowService
from ..testutils.constants import DIALOGFLOW_PROJECT_ID, DIALOGFLOW_LANGUAGE_CODE_EN, DIALOGFLOW_FALLBACK_RESPONSE

class TestDialogflowService(unittest.TestCase):

    def setUp(self):
        self.dialogflow_service = DialogflowService()

    """
    Tests for correct intents detected using exactly-defined
    training phrases on Dialogflow ES console
    """
    def test_detectIntent_exactTrainingPhrases(self):
        session_id = str(uuid.uuid4())

        get_user_by_id_intent_text = "get json for user ID auth0|12345678"
        detected_intent = self.dialogflow_service.detect_intent_texts(
            DIALOGFLOW_PROJECT_ID, 
            session_id, 
            get_user_by_id_intent_text, 
            DIALOGFLOW_LANGUAGE_CODE_EN)[0]

        self.assertEquals(detected_intent, "GetUserByIdIntent")

        search_user_by_email_intent_text = "search for jane.doe@test.au"

        detected_intent = self.dialogflow_service.detect_intent_texts(
            DIALOGFLOW_PROJECT_ID, 
            session_id, 
            search_user_by_email_intent_text, 
            DIALOGFLOW_LANGUAGE_CODE_EN)[0]

        self.assertEquals(detected_intent, "SearchUsersByEmailIntent")


    """
    Tests for correct intents detected using reasonable variations of
    training phrases on Dialogflow ES console
    """
    def test_detectIntent_fuzzyMatchQueries(self):
        session_id = str(uuid.uuid4())

        get_user_by_id_intent_text = "retrieve configs usr id auth0|12345678"
        detected_intent = self.dialogflow_service.detect_intent_texts(
            DIALOGFLOW_PROJECT_ID, 
            session_id, 
            get_user_by_id_intent_text, 
            DIALOGFLOW_LANGUAGE_CODE_EN)[0]

        self.assertEquals(detected_intent, "GetUserByIdIntent")

        search_user_by_email_intent_text = "find me details for jane.doe@test.au"

        detected_intent = self.dialogflow_service.detect_intent_texts(
            DIALOGFLOW_PROJECT_ID, 
            session_id, 
            search_user_by_email_intent_text, 
            DIALOGFLOW_LANGUAGE_CODE_EN)[0]

        self.assertEquals(detected_intent, "SearchUsersByEmailIntent")

    """
    If a query looks almost like it can match the correct intent but there is a malformed identifier,
    check if the fulfillment text recognises the missing args. In this case, the actual intent detected
    is non-deterministic, but at the very least we should identify missing args
    """
    def test_detectIntent_invalidIdentifiers(self):
        session_id = str(uuid.uuid4())

        get_user_by_id_intent_text = "retrieve configs usr id auth0-12345678"
        fulfillment_text = self.dialogflow_service.detect_intent_texts(
            DIALOGFLOW_PROJECT_ID, 
            session_id, 
            get_user_by_id_intent_text, 
            DIALOGFLOW_LANGUAGE_CODE_EN)[1]

        self.assertEquals(fulfillment_text, DIALOGFLOW_FALLBACK_RESPONSE)

        search_user_by_email_intent_text = "find me details for jane.doe(at)test.au"

        fulfillment_text = self.dialogflow_service.detect_intent_texts(
            DIALOGFLOW_PROJECT_ID, 
            "session_id", 
            search_user_by_email_intent_text, 
            DIALOGFLOW_LANGUAGE_CODE_EN)[1]

        self.assertEquals(fulfillment_text, DIALOGFLOW_FALLBACK_RESPONSE)
    
    def test_detectIntent_invalidQuery(self):
        session_id = str(uuid.uuid4())
        invalid_queries = ["spam and eggs", "hello", "goodbye", "f"]

        for text in invalid_queries:
            detected_intent = self.dialogflow_service.detect_intent_texts(
            DIALOGFLOW_PROJECT_ID, 
            session_id, 
            text, 
            DIALOGFLOW_LANGUAGE_CODE_EN)[0]

            self.assertEquals(detected_intent, "Default Fallback Intent")