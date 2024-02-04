import os
from simpleaichat import AIChat
from uuid import uuid4  # For generating a unique session ID

# Ensure your OpenAI API key is stored securely,
# Note: Hardcoding API keys in your code is not recommended for production environments.
api_key = "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"

# Ask for a session ID or generate a new one
session_id = input("Enter a session ID to continue a conversation, or press Enter to start a new one: ").strip()
if not session_id:
    session_id = str(uuid4())  # Generate a new, unique session ID
    print(f"No session ID provided. Starting a new conversation with session ID: {session_id}")

# Initialize the AIChat with your OpenAI API key, a system prompt, and the session ID
ai = AIChat(api_key=api_key, model="gpt-4-1106-preview", system="You are a helpful assistant.", id=session_id)

print("\nStart chatting with the assistant (type 'EOF' on a new line to send your message, type 'quit' to stop):")

while True:
    input_lines = []
    print("\nEnter your message:")
    while True:
        line = input()
        if line == "EOF":  # Use "EOF" to signal the end of your input
            print("Sending message to AIChat...")
            break
        input_lines.append(line)
    message = "\n".join(input_lines)

    if message.lower() == 'quit':
        print("Exiting chat.")
        break

    # Send message to AIChat and print response
    response = ai(message)
    print("\nAssistant:", response)
