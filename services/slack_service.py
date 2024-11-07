import os
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

# Initialize the Slack app with secrets from the environment
app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"), 
    token=os.getenv("SLACK_TOKEN")
)

app_handler = SlackRequestHandler(app)

@app.message("")
def handle_message(message, say):
    print("test")
    say(f"Hey hello there <@{message['user']}>!")

@app.command("/echo")
def repeat_text(ack, respond, command):
    # Acknowledge command request
    print(command)
    ack()
    respond(f"{command['text']}")