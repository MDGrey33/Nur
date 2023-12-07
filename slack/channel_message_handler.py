

class ChannelMessageHandler(SlackEventHandler):
    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        try:
            if req.type == "events_api":
                event = req.payload.get("event", {})
                if event.get("type") == "message" and "subtype" not in event and event.get("user") != bot_user_id:
                    text = event.get("text", "")
                    channel_id = event["channel"]

                    if "?" in text:
                        file_name = f"{channel_id}_context.txt"
                        self.answer_question(file_name, text, event.get("ts"), web_client, channel_id)
                    else:
                        # Respond to the message as usual
                        response_message = "Your usual response message here"
                        web_client.chat_postMessage(channel=channel_id, text=response_message)

        except Exception as e:
            logging.error(f"Error processing event: {e}", exc_info=True)

    def answer_question(self, file_name, question, message_id_to_reply_under, web_client, channel_id):
        # Fetch context from recent messages
        recent_messages = self.fetch_recent_messages(channel_id, web_client)
        context = "\n".join(recent_messages)
        with open(file_name, 'w') as file:  # Save context to file
            file.write(context)

        # Combine context with the question for the LLM
        combined_input = f"{context}\n\nQuestion: {question}"
        response = get_response_from_assistant(combined_input, [file_name])
        web_client.chat_postMessage(channel=channel_id, text=response, thread_ts=message_id_to_reply_under)

    def fetch_recent_messages(self, channel_id, web_client):
        response = web_client.conversations_history(channel=channel_id, limit=100)
        return [msg.get('text') for msg in response.get('messages', [])]

