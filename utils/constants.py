# Dialogflow high-level constants
DIALOGFLOW_PROJECT_ID = "querybot-auth0"
DIALOGFLOW_LANGUAGE_CODE_EN = "en"

# Dialogflow params and intents
GET_USER_BY_ID_INTENT = "GetUserByIdIntent"
USER_ID_PARAM = "Auth0-User-ID"

SEARCH_USERS_BY_EMAIL_INTENT = "SearchUsersByEmailIntent"
EMAIL_PARAM = "email"

# String constants
MULTILINE_CODE_DELIMITER = "```"
NEWLINE_DELIMITER = "\n"
NO_DATA_MESSAGE = "Unfortunately, we couldn't find any data with that identifier"

# Slack constants
MAX_MESSAGE_LENGTH = 3800 # there's a limit for 4000, reduce a little to account for initial fulfilment text