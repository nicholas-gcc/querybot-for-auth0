import os
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_sdk.errors import SlackApiError
from ..controllers.message_controller import MessageController

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

    # Check if the payload needs to be uploaded as a file
    if response.get('needs_file_upload'):
        # Send the initial text response
        say(text=response['text'])

        try:
            # Upload the payload as a file and share it in the channel
            app.client.files_upload_v2(
                channels=[channel_id],
                content=response['payload'],
                filename="response.txt",
                title="Response"
            )
        except SlackApiError as e:
            say(text=f"Failed to upload the file: {e.response['error']}")
    else:
        # Combine the text and payload
        combined_message = response['text']
        if response['payload']:
            combined_message += f"\n{response['payload']}"

        # Send the combined message
        say(text=combined_message)