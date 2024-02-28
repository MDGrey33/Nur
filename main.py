# ./main.py
from confluence_integration.retrieve_space import get_space_content, choose_space
from vector.chroma_threads import retrieve_relevant_documents
from oai_assistants.query_assistant_from_documents import query_assistant_with_context
from gpt_4t.query_from_documents_threads import query_gpt_4t_with_context
from confluence_integration.extract_page_content_and_store_processor import get_page_content_using_queue
from confluence_integration.extract_page_content_and_store_processor import embed_pages_missing_embeds
from qa_syncup.sync_up_qa_articles_to_confluence import sync_up_interactions_to_confluence
from slack.channel_interaction import load_slack_bot
from datetime import datetime
from database.space_manager import SpaceManager
from vector.create_vector_db import add_embeds_to_vector_db
from oai_assistants.openai_assistant import load_manage_assistants
from interactions.vectorize_and_store import vectorize_interactions_and_store_in_db


def load_new_documentation_space():
    space_key, space_name = choose_space()
    if space_key and space_name:
        print("Retrieving space content...")
        get_space_content(space_key)
        get_page_content_using_queue(space_key)
        embed_pages_missing_embeds()
        space_manager = SpaceManager()
        last_import_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        space_manager.upsert_space_info(space_key, space_name, last_import_date)
        add_embeds_to_vector_db(space_key)
        print(f"\nSpace '{space_name}' retrieval and indexing complete.")
    print("\nSpace retrieval and indexing complete.")


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
        print("4. Create a vector db for interactions")
        print("5. Start Slack Bot")
        print("6. Manage assistants")
        print("0. Cancel/Quit")
        choice = input("Enter your choice (0-6): ")

        if choice == "1":
            print("Loading new documentation space...")
            load_new_documentation_space()

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
            print("Creating vector db for interactions")
            vectorize_interactions_and_store_in_db()

        elif choice == "5":
            print("Starting Slack Bot Using Assistants and fast API...")
            # Run the FastAPI server
            input("Started the FastAPI server located at './api/endpoint' and Press Enter to continue.")
            # Start the Slack bot in the main thread
            load_slack_bot()
            print("Slack Bot is running in parallel processing mode.")

        elif choice == "6":
            load_manage_assistants()

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