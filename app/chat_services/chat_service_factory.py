# /app/factories/chat_service_factory.py

from app.chat_services.slack.slack_service import SlackService
from app.chat_services.chat_service_interface import ChatServiceInterface


class ChatServiceFactory:

    @staticmethod
    def get_service(service_name: str) -> ChatServiceInterface:
        if service_name == "slack":
            return SlackService()
        else:
            raise ValueError(f"Service {service_name} is not supported.")
