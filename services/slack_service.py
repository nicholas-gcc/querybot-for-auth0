import logging
import os

from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_sdk.errors import SlackApiError

from ..controllers.message_controller import MessageController
from ..dao.m2m_credentials_dao import m2m_credentials_dao
from ..utils.constants import (
    AUTH0_CREDENTIALS_SAVED_MESSAGE,
    CREDENTIALS_MODAL_CALLBACK_ID,
    HELP_TEXT,
)

# Set up logging
logger = logging.getLogger(__name__)

# Retrieve Slack credentials from environment variables
SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")

if not SIGNING_SECRET or not SLACK_TOKEN:
    logger.error("Slack signing secret or token is not set in environment variables.")
    raise ValueError("Slack signing secret or token is not set.")

# Initialize the Slack app with secrets from the environment
app = App(
    signing_secret=SIGNING_SECRET,
    token=SLACK_TOKEN,
)

app_handler = SlackRequestHandler(app)

message_controller = MessageController()


@app.event("message")
def handle_message_events(event: dict, say):
    """
    Processes message events and determines response and optional file upload if needed.

    Args:
        event (dict): The event payload from Slack.
        say (callable): Function to send a message back to Slack.
    """
    slack_user_id = event.get('user')
    user_message = event.get('text')
    channel_id = event.get('channel')

    logger.debug(
        f"Received message event from user {slack_user_id} in channel {channel_id}: {user_message}"
    )

    # Input validation
    if not user_message or not slack_user_id:
        logger.error("Missing user message or Slack user ID in event.")
        return

    # Process the message
    try:
        response = message_controller.process_message(user_message, slack_user_id)
    except Exception as e:
        logger.exception("Error processing message.")
        say(text="An error occurred while processing your message. Please try again later.")
        return

    # Prepare the message text
    message_text = response.get('text', '')
    additional_text = response.get('additional_text')
    if additional_text:
        message_text += f"\n{additional_text}"

    # Check if the payload needs to be uploaded as a file
    if response.get('needs_file_upload'):
        # Send the initial text response without the payload
        say(text=message_text)

        try:
            # Upload the payload as a file and share it in the channel
            app.client.files_upload_v2(
                channel=channel_id,
                content=response['payload'],
                filename="response.txt",
                title="Response",
            )
            logger.info(f"File uploaded successfully to channel {channel_id}.")
        except SlackApiError as e:
            logger.exception("Failed to upload file to Slack.")
            say(text=f"Failed to upload the file: {e.response['error']}")
    else:
        # Combine the text and payload
        if response.get('payload'):
            message_text += f"\n{response['payload']}"
        # Send the combined message
        say(text=message_text)
        logger.info(f"Sent message to channel {channel_id}.")


@app.command("/help")
def handle_help_command(ack, respond, command):
    """
    Handles the /help command by sending the help text.

    Args:
        ack (callable): Function to acknowledge the command request.
        respond (callable): Function to send a response to the command.
        command (dict): The command payload from Slack.
    """
    ack()
    respond(HELP_TEXT)
    logger.debug("Responded to /help command.")


@app.command("/authorize")
def open_credentials_modal(ack, body, client):
    """
    Opens the credentials modal for the user to submit their Auth0 credentials.

    Args:
        ack (callable): Function to acknowledge the command request.
        body (dict): The body of the request from Slack.
        client: The Slack WebClient.
    """
    ack()
    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view=credentials_modal_view(),
        )
        logger.debug(f"Opened credentials modal for user {body['user_id']}.")
    except SlackApiError as e:
        logger.exception("Failed to open credentials modal.")
        client.chat_postMessage(
            channel=body['user_id'],
            text="An error occurred while opening the credentials modal. Please try again later.",
        )


def credentials_modal_view() -> dict:
    """
    Returns the view definition for the credentials modal.

    Returns:
        dict: The modal view definition.
    """
    return {
        "type": "modal",
        "callback_id": CREDENTIALS_MODAL_CALLBACK_ID,
        "title": {"type": "plain_text", "text": "Auth0 Credentials"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "blocks": [
            {
                "type": "input",
                "block_id": "base_url_block",
                "label": {"type": "plain_text", "text": "Auth0 Base URL"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "base_url_input",
                },
            },
            {
                "type": "input",
                "block_id": "client_id_block",
                "label": {"type": "plain_text", "text": "Client ID"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "client_id_input",
                },
            },
            {
                "type": "input",
                "block_id": "client_secret_block",
                "label": {"type": "plain_text", "text": "Client Secret"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "client_secret_input",
                },
            },
        ],
    }


@app.view(CREDENTIALS_MODAL_CALLBACK_ID)
def handle_credentials_submission(ack, body, client, view):
    """
    Handles the submission of the credentials modal.

    Args:
        ack (callable): Function to acknowledge the view submission.
        body (dict): The body of the request from Slack.
        client: The Slack WebClient.
        view (dict): The view payload from Slack.
    """
    ack()
    slack_user_id = body['user']['id']
    values = view['state']['values']

    try:
        base_url = values['base_url_block']['base_url_input']['value']
        client_id = values['client_id_block']['client_id_input']['value']
        client_secret = values['client_secret_block']['client_secret_input']['value']

        # Validate inputs
        if not base_url or not client_id or not client_secret:
            raise ValueError("All fields are required.")

        # Save credentials to MongoDB
        m2m_credentials_dao.upsert_credentials(
            slack_user_id,
            {
                'auth0_base_url': base_url,
                'auth0_client_id': client_id,
                'auth0_client_secret': client_secret,
                'access_token': None,
                'token_expires_at': None,
            },
        )
        logger.info(f"Auth0 credentials saved for user {slack_user_id}.")

        # Confirm to the user
        client.chat_postMessage(
            channel=slack_user_id,
            text=AUTH0_CREDENTIALS_SAVED_MESSAGE,
        )
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        client.chat_postMessage(
            channel=slack_user_id,
            text="Please fill in all required fields.",
        )
    except Exception as e:
        logger.exception("Error saving Auth0 credentials.")
        client.chat_postMessage(
            channel=slack_user_id,
            text="An error occurred while saving your credentials. Please try again.",
        )

