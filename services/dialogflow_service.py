import logging
from typing import Tuple

from google.cloud import dialogflow_v2 as dialogflow
from google.protobuf.json_format import MessageToDict

from ..utils.constants import (
    DIALOGFLOW_LANGUAGE_CODE_DEFAULT,
    DIALOGFLOW_TIMEOUT,
)

logger = logging.getLogger(__name__)


class DialogflowService:
    """Service for interacting with Google Dialogflow API."""

    def __init__(self):
        """Initialize the DialogflowService."""
        self.session_client = dialogflow.SessionsClient()

    def detect_intent_texts(
        self,
        project_id: str,
        session_id: str,
        text: str,
        language_code: str = DIALOGFLOW_LANGUAGE_CODE_DEFAULT,
    ) -> Tuple[str, str, dict]:
        """
        Detect the intent of a text input using Dialogflow.

        Args:
            project_id (str): The Google Cloud project ID.
            session_id (str): A unique identifier for the Dialogflow session.
            text (str): The user's input text.
            language_code (str, optional): The language code of the input text. Defaults to 'en'.

        Returns:
            tuple: A tuple containing:
                - detected_intent (str): The name of the detected intent.
                - fulfillment_text (str): The fulfillment text from Dialogflow.
                - parameters (dict): The parameters extracted by Dialogflow.

        Raises:
            Exception: If an error occurs during intent detection.
        """
        try:
            # Input validation
            if not text:
                logger.error("Input text is empty.")
                raise ValueError("Input text must not be empty.")

            if not project_id or not session_id:
                logger.error("Project ID or session ID is missing.")
                raise ValueError("Project ID and session ID are required.")

            session = self.session_client.session_path(project_id, session_id)

            text_input = dialogflow.TextInput(text=text, language_code=language_code)
            query_input = dialogflow.QueryInput(text=text_input)

            logger.debug(
                f"Detecting intent for session {session_id} with text: {text}"
            )

            response = self.session_client.detect_intent(
                request={"session": session, "query_input": query_input},
                timeout=DIALOGFLOW_TIMEOUT,
            )

            # Convert Protobuf response to a dictionary
            response_dict = MessageToDict(response._pb)

            detected_intent = response_dict["queryResult"]["intent"]["displayName"]
            fulfillment_text = response_dict["queryResult"]["fulfillmentText"]
            parameters = response_dict["queryResult"].get("parameters", {})

            logger.debug(
                f"Detected intent: {detected_intent}, Parameters: {parameters}"
            )

            return detected_intent, fulfillment_text, parameters

        except Exception as e:
            logger.exception("Error detecting intent with Dialogflow")
            raise

