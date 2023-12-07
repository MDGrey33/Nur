import logging
import time
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from credentials import slack_bot_user_oauth_token, slack_app_level_token

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)

# Initialize a Web client
web_client = WebClient(token=slack_bot_user_oauth_token)

# Your bot's user ID
bot_user_id = "U069C17DCE5"  # Replace with your bot's actual user ID


# Function to handle events
def process(client: SocketModeClient, req: SocketModeRequest):
    try:
        logging.debug(f"Received event: {req.payload}")
        if req.type == "events_api":
            event = req.payload.get("event", {})
            logging.info(f"Event details: {event}")

            # Respond to any message that is not from a bot
            if event.get("type") == "message" and "subtype" not in event and event.get("user") != bot_user_id:
                text = event.get("text", "")
                channel_id = event["channel"]
                logging.info(f"Message received: '{text}' in channel {channel_id}")

                # Craft the response message
                response_message = f"I got a message from you saying \"{text}\""
                web_client.chat_postMessage(channel=channel_id, text=response_message)
                logging.info(f"Sent response in channel {channel_id}")

            # Acknowledge the event to Slack
            client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
    except Exception as e:
        logging.error(f"Error processing event: {e}", exc_info=True)


# Initialize Socket Mode client
socket_mode_client = SocketModeClient(app_token=slack_app_level_token, web_client=web_client)

# Attach the event handler
socket_mode_client.socket_mode_request_listeners.append(process)

# Start listening to Slack events
socket_mode_client.connect()

# Keep the process alive
try:
    while True:
        logging.debug("Bot is running...")
        time.sleep(10)  # Sleep for 10 seconds
except KeyboardInterrupt:
    logging.info("Bot stopped by the user")
except Exception as e:
    logging.critical("Bot stopped due to an exception", exc_info=True)
