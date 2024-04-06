# /app/services/slack_service.py

from app.chat_services.chat_service_interface import ChatServiceInterface

# should be replaced with a new implementation, maybe a copy of the slack folder here
from slack.bot import load_slack_bot


class SlackService(ChatServiceInterface):

    def start_service(self):
        load_slack_bot()
        print("Slack service started.")
