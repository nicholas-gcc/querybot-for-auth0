import os
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_sdk.errors import SlackApiError
from ..controllers.message_controller import MessageController
from ..utils.constants import HELP_TEXT

# Initialize the Slack app with secrets from the environment
app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"), 
    token=os.getenv("SLACK_TOKEN")
)

app_handler = SlackRequestHandler(app)

message_controller = MessageController()

@app.event("message")
def handle_message_events(event, say):
    """
    Processes message event and determines response and optional file upload if needed
    """
    user_message = event.get('text')
    channel_id = event.get('channel')
    
    response = message_controller.process_message(user_message)

    # Prepare the message text
    message_text = response['text']
    if response.get('additional_text'):
        message_text += f"\n{response['additional_text']}"

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
                title="Response"
            )
        except SlackApiError as e:
            say(text=f"Failed to upload the file: {e.response['error']}")
    else:
        # Combine the text, additional_text, and payload
        if response.get('payload'):
            message_text += f"\n{response['payload']}"
        # Send the combined message
        say(text=message_text)

@app.command("/help")
def handle_help_command(ack, respond, command):
    ack()
    respond(HELP_TEXT)

@app.command("/authorize")
def handle_authorize_command(body, ack, client, logger):
    ack()
    res = client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "authorize-modal",
            "title": {"type": "plain_text", "text": "Auth0 Details"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "base_url",
                    "element": {"type": "plain_text_input", "action_id": "my_action"},
                    "label": {"type": "plain_text", "text": "Auth0 Tenant Base URL"},
                },
                {
                    "type": "input",
                    "block_id": "client_id",
                    "element": {"type": "plain_text_input", "action_id": "my_action"},
                    "label": {"type": "plain_text", "text": "Auth0 M2M Client ID"},
                },
                {
                    "type": "input",
                    "block_id": "client_secret",
                    "element": {"type": "plain_text_input", "action_id": "my_action"},
                    "label": {"type": "plain_text", "text": "Auth0 M2M Client Secret"},
                }
            ],
        },
    )
