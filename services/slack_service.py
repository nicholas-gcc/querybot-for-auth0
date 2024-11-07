import os
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
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
    print(event)
    user_message = event.get('text')
    
    response = message_controller.process_message(user_message)

    # Send response back to Slack
    say(response)