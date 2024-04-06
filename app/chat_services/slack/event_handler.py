from abc import ABC, abstractmethod


class SlackEventHandler(ABC):
    @abstractmethod
    def handle(self, client, req, web_client, bot_user_id):
        print("Handling Slack events")
