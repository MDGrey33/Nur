# /nurai/chat_services/slack/event_handlers/reaction_handlers/reaction_handlers.py
from nurai.chat_services.slack.event_handlers.event_handler import SlackEventHandler
from nurai.logger.logger import setup_logger
from nurai.events.models.events import BookmarkEvent
import requests

# The package name is automatically deduced
logging = setup_logger()


class ReactionAddedHandler(SlackEventHandler):
    def handle(self, client, req, web_client, bot_user_id):
        logging.info("Reaction on a message received")

        # Correctly access the event data from the SocketModeRequest payload
        event_data = req.payload.get("event", {})
        reaction_type = event_data.get("reaction")
        logging.info(f"Reaction type received: {reaction_type}")

        # Process the 'bookmark' reaction
        if reaction_type == "bookmark":
            logging.info("Reaction identified to be bookmark")
            # Extract necessary data from the event_data to create a BookmarkEvent
            bookmark_event = BookmarkEvent(
                reaction=reaction_type,
                ts=event_data["item"]["ts"],
                thread_ts=event_data.get("item", {}).get("thread_ts", ""),
                channel=event_data["item"]["channel"],
                user=event_data["user"],
            )
            logging.info(f"Calling API with bookmark event {bookmark_event.dict()}")
            # Assuming the API is hosted locally and the endpoint matches the FastAPI route
            response = requests.post(
                "http://localhost:8000/events/bookmarks", json=bookmark_event.dict()
            )
            logging.info("API called")
            logging.info(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                print("Bookmark event processed successfully.")
            else:
                print("Failed to process bookmark event.")
        else:
            # Handle other reactions as before
            logging.info("Handling other reaction on a message")
