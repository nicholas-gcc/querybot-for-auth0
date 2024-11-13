# querybot-for-auth0

This app allows you to send a query on Slack, using natural language processing to understand your request and fetches the relevant data from Auth0. Simply send a message to the bot with your query in plain English.

## Table of Contents

- [Rationale](#rationale)
- [Features](#features)
  - [Supported queries](#supported-queries)
- [Setup](#setup)
- [Technical Architecture](#technical-architecture)
- [Roadmap](#roadmap)

## Rationale

- I'm looking to make Auth0 data more accessible to Auth0 customers' non-technical (or even technical) staff and help them get data on the fly
- For some of our Auth0 customers, there are teams that are non-technical in nature, or seldom use Auth0 primarily but may need data sometimes. There are some obstacles, including but not limited to:
  - Having no access to their Auth0 tenant as it's reserved for certain teams
  - Lack of technical know-how to perform a `cURL` request
  - Unfamiliarity with Dashboard UI making navigation and data retrieval slower
- For less technical staff, asking "Please get me my tenant configurations" comes more naturally than:
```
curl -L 'https://<YOUR_TENANT_DOMAIN>.<REGION>.auth0.com/api/v2/tenants/settings' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer 🔒'
```
- Why not find a way to simplify the way we communicate with Auth0 via Slack and make it possible to ask for data in a natural human-readable language?

## Features

- Interactive Slack-based chatbot that parses plain English messages from Slack, uses [Dialogflow](https://cloud.google.com/products/conversational-agents?hl=en) to match it to the correct [Auth0 Management API](https://auth0.com/docs/api/management/v2/introduction) call

- Ability to parse intents and account for variations in messaging, pick up key parameters (e.g. email, date, user ID) and even parse relative dates and differing date formats (e.g. "Get me daily stats from last week", "Retrieve daily stats from 2 months ago", "...from Jan 1 to Mar 16" etc.) and resolve them to the correct intended API call with the correct query parameters

- Support for a slash command `/help` to display user instructions

- (IN FUTURE) Support for a slash command `/authorize` to render a modal where users can input Auth0 domain and client credentials to perform client credentials calls and dynamically configure their tenant configs

### Supported queries
- **Get User Details By ID** (Retrieve user details given an Auth0 user ID)
  - <em>Usage examples<em>:
    - "Get user details for user ID `auth0|6724489270033bac7e8e0c0c`"
    - "pls gimme raw json for `samlp|Okta-SAML-SP|nicholas.canete@okta.com`"
      
- **Get Daily Stats** (Retrieve daily statistics within an optional date range)
  - <em>Usage examples<em>:
    - "Get daily stats"
    - "Please retrieve daily stats from Jan 1 to Mar 14"
    - "Show stats for last week"
    - "Retrieve daily statistics since from the past 3 months"
    - Subtle note on messaging - Dialogflow will resolve `...X weeks ago` resolve to a startDate of X weeks ago, and endDate to X + 1 weeks ago. If you want X weeks ago to present, say `...for the past X weeks`<em>
    
- **Get Tenant Settings** (Retrieve your tenant's settings)
  - <em>Usage examples<em>:
    - "Show tenant settings"
    - "Display the tenant's configurations"
   
- **Get Active Users Count** (Get the number of active users in the last 30 days.)
  - <em>Usage examples<em>:
    - "How many active users do we have?"
    - "What's our MAU count?"
   
- **Search User By Email** (Find user details using an email address.)
  - <em>Usage examples<em>:
    - "Find user with email nicholasgcc@gmail.com"
    - "Search for user by email jane.doe@company.com."
   
## Setup (running your own local instance)

This is a work in progress :)

## Technical Architecture

![image](https://github.com/user-attachments/assets/e97471d2-65b1-4a26-8349-c7e91804e3b4)

## Roadmap

- Set up the slash command `/authorize` on Slack to enable users to change tenants / M2M apps performing client credentials calls on the fly. Currently, this operates off environmental variables on a `.env` file
  
- Add persistent storage to map users to a current instance of Auth0 configs to support multiple users
  
- Deploy API a more robust platform (e.g. Docker, AWS Lambda)

- Release app officially on Slack marketplace

- Add support for more API operations (e.g. Get Connections, Get Applications, Get Roles, etc.)

- Set up proper CI/CD

