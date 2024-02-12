from confluence_integration.retrieve_space import get_space_content
from vector.chroma_threads import retrieve_relevant_documents
from oai_assistants.query_assistant_from_documents import query_assistant_with_context
from gpt_4t.query_from_documents_threads import query_gpt_4t_with_context
from confluence_integration.extract_page_content_and_store_processor import get_page_content_using_queue, choose_space
from vector.vectorize_and_persist_processor import process_vectorization_queue
from qa_syncup.sync_up_qa_articles_to_confluence import sync_up_interactions_to_confluence
from slack.channel_interaction import load_slack_bot
from slack.channel_interaction_assistants import load_slack_bot as load_slack_bot_assistant
from datetime import datetime
from database.space_manager import SpaceManager


def add_space():
    '''
    Add a new space to the system, process its content, and store its information.
    :return: space_key
    '''
    space_key = None
    try:

        space_key = choose_space()  # Let the user choose a space.
        if space_key:
            print("Retrieving space content...")
            # Additional logic to retrieve space name and last import date as needed
            space_name = "Example Space Name"  # This should be dynamically retrieved
            last_import_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Example timestamp, adjust as necessary

            get_space_content(space_key)  # Retrieve content for the chosen space.
            print("Processing content...")
            space_key = get_page_content_using_queue(space_key)  # Process the retrieved content.
            print("Vectorizing content...")
            process_vectorization_queue(space_key)  # Vectorize the processed content for search.

            # Store space information in the database
            space_manager = SpaceManager()
            space_manager.add_space_info(space_key, space_name, last_import_date)
            print(f"\nSpace '{space_name}' retrieval and indexing complete.")
    except Exception as e:
        print(f"An error occurred while adding the space: {e}")
    return space_key


def update_spaces():
    '''
    Update all existing spaces from their last update date
    :return:
    '''
    pass


def answer_question_with_assistant(question):
    relevant_document_ids = retrieve_relevant_documents(question)
    response, thread_id = query_assistant_with_context(question, relevant_document_ids)
    return response, thread_id


def answer_question_with_gpt_4t(question):
    relevant_document_ids = retrieve_relevant_documents(question)
    response = query_gpt_4t_with_context(question, relevant_document_ids)
    return response


def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Load New Documentation Space")
        print("2. Ask a Question to GPT-4T Assistant")
        print("3. Ask a question to GPT-4T")
        print("4. Sync up QA articles to Confluence")
        print("5. Start Slack Bot Using Assistants API")
        print("6. Start Slack Bot Using Assistant")
        print("0. Cancel/Quit")
        choice = input("Enter your choice (0-6): ")

        if choice == "1":
            space_key = choose_space()
            get_space_content(space_key)
            get_page_content_using_queue(space_key)
            process_vectorization_queue(space_key)
            print("\nSpace retrieval and indexing complete.")

        if choice == "7":
            space_key = choose_space()
            get_space_content(space_key)
            get_page_content_using_queue(space_key)
            # process_vectorization_queue(space_key)
            print("\nSpace retrieval and indexing complete No vector db created.")

        elif choice == "2":
            question = ask_question()
            if question:
                answer, thread_id = answer_question_with_assistant(question)
                print(f"\nThread ID: {thread_id}\nAnswer: {answer}")

        elif choice == "3":
            question = ask_question()
            if question:
                answer = answer_question_with_gpt_4t(question)
                print("\nAnswer:", answer)

        elif choice == "4":
            print("Syncing up QA articles to Confluence...")
            sync_up_interactions_to_confluence()

        elif choice == "5":
            print("Starting Slack Bot Using Assistants API...")
            # Run the FastAPI server
            input("Have you started the FastAPI server './api/endpoint'? Press Enter to continue.")
            # Start the Slack bot in the main thread
            load_slack_bot()
            print("Slack Bot is running in parallel processing mode.")

        elif choice == "6":
            print("Starting Slack Bot...")
            load_slack_bot_assistant()
            print("Slack Bot is running in parallel processing mode.")

        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter 0, 1, 2, 3, 4, 5 or 6.")


def ask_question():
    print("\nEnter your question (type 'done' on a new line to submit, 'quit' to cancel):")
    lines = []
    while True:
        line = input()
        if line.lower() == "done":
            return "\n".join(lines)
        elif line.lower() == "quit":
            return None
        else:
            lines.append(line)


if __name__ == "__main__":
    main_menu()