from google.cloud import dialogflow

class DialogflowService:

    def detect_intent_texts(self, project_id, session_id, text, language_code):
        session_client = dialogflow.SessionsClient()

        session = session_client.session_path(project_id, session_id)

        print(text)

        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        detected_intent = response.query_result.intent.display_name

        fulfillment_text = response.query_result.fulfillment_text

        return detected_intent, fulfillment_text
