import logging
import uuid

from ..dao.m2m_credentials_dao import m2m_credentials_dao
from ..services.auth0_service import Auth0Service
from ..services.dialogflow_service import DialogflowService
from ..services.intent_handlers.intent_handler_factory import IntentHandlerFactory
from ..utils.constants import (
    AUTH0_CREDENTIALS_PROMPT,
    DIALOGFLOW_LANGUAGE_CODE_EN,
    DIALOGFLOW_PROJECT_ID,
)
from ..utils.string_utils import StringUtils

logger = logging.getLogger(__name__)


class MessageController:
    """Controller for processing incoming Slack messages and generating responses."""

    def __init__(self):
        """Initialize the MessageController with necessary services."""
        self.dialogflow_service = DialogflowService()
        self.intent_handler_factory = IntentHandlerFactory()

    def process_message(self, message: str, slack_user_id: str) -> dict:
        """
        Process an incoming message from Slack.

        Args:
            message (str): The message text received from Slack.
            slack_user_id (str): The Slack user ID of the sender.

        Returns:
            dict: A response dictionary containing text, payload, and flags.
        """
        logger.debug(f"Processing message from user {slack_user_id}: {message}")

        # Validate inputs
        if not message or not slack_user_id:
            logger.error("Message or Slack user ID is missing.")
            return self._error_response(
                "Invalid input. Please provide a valid message and Slack user ID."
            )

        # Remove markdown formatting coming in from Slack
        sanitized_message = StringUtils().remove_format(message)

        # Since we have defined single-turn agents, session can be arbitrary
        dialogflow_session_id = uuid.uuid4()

        # Detect intent using Dialogflow
        try:
            detected_intent, fulfillment_text, parameters = (
                self.dialogflow_service.detect_intent_texts(
                    DIALOGFLOW_PROJECT_ID,
                    dialogflow_session_id,
                    sanitized_message,
                    DIALOGFLOW_LANGUAGE_CODE_EN,
                )
            )
            logger.debug(f"Detected intent: {detected_intent}, Parameters: {parameters}")
        except Exception as e:
            logger.exception("Error detecting intent with Dialogflow")
            return self._error_response(
                "Sorry, I couldn't process your message right now. Please try again later."
            )

        # Retrieve user's Auth0 credentials from MongoDB
        user_credentials = m2m_credentials_dao.get_credentials(slack_user_id)
        if not user_credentials:
            logger.info(f"No Auth0 credentials found for user {slack_user_id}")
            # Prompt user to provide credentials via the /auth0_credentials command
            return self._simple_response(AUTH0_CREDENTIALS_PROMPT)

        # Instantiate Auth0Service with the user's credentials
        try:
            auth0_service = Auth0Service(
                auth0_base_url=user_credentials['auth0_base_url'],
                client_id=user_credentials['auth0_client_id'],
                client_secret=user_credentials['auth0_client_secret'],
                slack_user_id=user_credentials['slack_user_id'],
                access_token=user_credentials.get('access_token'),
                token_expires_at=user_credentials.get('token_expires_at'),
            )
            auth0_service.slack_user_id = slack_user_id  # For updating tokens in MongoDB
        except KeyError as e:
            logger.exception(
                f"Missing Auth0 credential key for user {slack_user_id}: {e}"
            )
            return self._simple_response(
                "Your Auth0 credentials are incomplete. Please update them using the `/auth0_credentials` command."
            )

        # Get the appropriate intent handler
        handler = self.intent_handler_factory.get_handler(detected_intent)

        if handler:
            logger.debug(f"Found handler for intent: {detected_intent}")
            # Pass the user's credentials to the intent handler
            try:
                handler_result = handler.handle_intent(parameters, auth0_service)
            except Exception as e:
                logger.exception("Error in intent handler")
                return self._error_response(
                    "An error occurred while processing your request. Please try again later."
                )

            # Handle the result from the intent handler
            payload, needs_file_upload, additional_text = self._parse_handler_result(
                handler_result
            )

            response = {
                'text': fulfillment_text,
                'payload': payload,
                'needs_file_upload': needs_file_upload,
                'additional_text': additional_text,
            }
        else:
            logger.info(f"No handler found for intent: {detected_intent}")
            # Fallback response if no handler is found
            response = {
                'text': fulfillment_text,
                'payload': None,
                'needs_file_upload': False,
                'additional_text': None,
            }

        logger.debug(f"Response: {response}")
        return response

    @staticmethod
    def _parse_handler_result(handler_result):
        """
        Parse the result returned by the intent handler.

        Args:
            handler_result (tuple or any): The result from the intent handler.

        Returns:
            tuple: A tuple containing payload, needs_file_upload, and additional_text.
        """
        if isinstance(handler_result, tuple):
            if len(handler_result) == 3:
                payload, needs_file_upload, additional_text = handler_result
            elif len(handler_result) == 2:
                payload, needs_file_upload = handler_result
                additional_text = None
            else:
                payload = handler_result
                needs_file_upload = False
                additional_text = None
        else:
            payload = handler_result
            needs_file_upload = False
            additional_text = None

        return payload, needs_file_upload, additional_text

    @staticmethod
    def _error_response(text):
        """
        Generate a standardized error response.

        Args:
            text (str): The error message to send to the user.

        Returns:
            dict: A response dictionary containing the error message.
        """
        return {
            'text': text,
            'payload': None,
            'needs_file_upload': False,
            'additional_text': None,
        }

    @staticmethod
    def _simple_response(text):
        """
        Generate a standardized simple response.

        Args:
            text (str): The message to send to the user.

        Returns:
            dict: A response dictionary containing the message.
        """
        return {
            'text': text,
            'payload': None,
            'needs_file_upload': False,
            'additional_text': None,
        }
