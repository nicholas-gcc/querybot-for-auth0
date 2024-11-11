import os

DIALOGFLOW_PROJECT_ID = "querybot-auth0"
DIALOGFLOW_LANGUAGE_CODE_EN = "en"
DIALOGFLOW_FALLBACK_RESPONSE = "You must specify a valid argument to execute this query"
AUTH0_BASE_URL = os.getenv("AUTH0_BASE_URL")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

