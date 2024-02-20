# ./credentials.py
import os

confluence_credentials = {'base_url': os.environ.get("CONFLUENCE_BASE_URL"),
                          'username': os.environ.get("CONFLUENCE_USER"),
                          'api_token': os.environ.get("CONFLUENCE_API_TOKEN"),
                          }

oai_api_key = os.environ.get("OPENAI_API_KEY")

# Slack tokens Toptal
slack_app_level_token = os.environ.get("SLACK_APP_TOKEN")
slack_bot_user_oauth_token = os.environ.get("SLACK_BOT_TOKEN")
slack_user_oauth_token = os.environ.get("SLACK_USER_TOKEN")
