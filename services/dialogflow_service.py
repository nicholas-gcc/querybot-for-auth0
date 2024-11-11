from google.cloud import dialogflow
from google.protobuf.json_format import MessageToDict


class DialogflowService:

    def detect_intent_texts(self, project_id, session_id, text, language_code):
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)

        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        
        # from https://stackoverflow.com/questions/71256960/how-to-access-infos-in-protobuf-response-from-dialogflow-api
        response = MessageToDict(response._pb)

        detected_intent = response["queryResult"]["intent"]["displayName"]
        fulfillment_text = response["queryResult"]["fulfillmentText"]
        parameters = response["queryResult"]["parameters"]

        return detected_intent, fulfillment_text, parameters
