# Dialogflow high-level constants
DIALOGFLOW_PROJECT_ID = "querybot-auth0"
DIALOGFLOW_LANGUAGE_CODE_EN = "en"

# Dialogflow params and intents
GET_USER_BY_ID_INTENT = "GetUserByIdIntent"
USER_ID_PARAM = "Auth0-User-ID"
GET_TENANT_SETTINGS_INTENT = "GetTenantSettingsIntent"
GET_ACTIVE_USERS_COUNT_INTENT = "GetActiveUsersCountIntent"
GET_STATS_INTENT = "GetStatsIntent"

SEARCH_USERS_BY_EMAIL_INTENT = "SearchUsersByEmailIntent"
EMAIL_PARAM = "email"
DATE_PERIOD_PARAM = "date-period"

# String constants
MULTILINE_CODE_DELIMITER = "```"
NEWLINE_DELIMITER = "\n"
NO_DATA_MESSAGE = "Unfortunately, we couldn't find any data with that identifier"

# Slack constants
MAX_MESSAGE_LENGTH = 3800 # there's a limit for 4000, reduce a little to account for initial fulfilment text

# Text response when calling /help
HELP_TEXT = """
*Auth0 Slack Bot Help*

Simply send a message to the bot with your query in plain English. This bot uses natural language processing to understand your request and fetches the relevant data from Auth0.

---

*Supported Queries*

1. *Get User Details by ID*
   - *Description:* Retrieve user details using a user ID.
   - *Usage Example:*
     - `"Get user details for user ID <user_id>"`
     - `"Get information on user auth0|abc123."`

2. *Get Daily Stats*
   - *Description:* Retrieve daily statistics within a date range.
   - *Usage Examples:*
     - `"Get daily stats from Jan 1 to Jan 7."`
     - `"Show stats for last week."`
     - `"Retrieve daily statistics since last Monday."`
   - *Note:* Supports unstructured and relative dates like "yesterday," "last month," etc.

3. *Get Tenant Settings*
   - *Description:* Retrieve your tenant's settings.
   - *Usage Example:*
     - `"Show tenant settings."`
     - `"Display the tenant's configurations."`

4. *Get Active Users Count*
   - *Description:* Get the number of active users in the last 30 days.
   - *Usage Example:*
     - `"How many active users do we have?"`
     - `"Show active users for the last 30 days."`

5. *Search User by Email*
   - *Description:* Find user details using an email address.
   - *Usage Example:*
     - `"Find user with email <email>"`
     - `Search for user by email jane.doe@company.com."`

---

*Note:* Replace `<user_id>` and `<email>` with the actual user ID and email address.

For more information and technical details, visit our <https://github.com/nicholas-gcc/querybot-for-auth0|GitHub repository>.
"""
