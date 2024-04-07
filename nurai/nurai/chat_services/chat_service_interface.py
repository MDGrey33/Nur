# /app/services/chat_service_interface.py

from abc import ABC, abstractmethod


class ChatServiceInterface(ABC):

    @abstractmethod
    def start_service(self):
        pass
