from confluence_integration.retrieve_space import get_space_content
from vector.chroma_threads import retrieve_relevant_documents, add_to_vector
from oai_assistants.query_assistant_from_documents import query_assistant_with_context
from gpt_4t.query_from_documents_threads import query_gpt_4t_with_context
from confluence_integration.extract_page_content_and_store_processor import get_page_content_using_queue
from vector.vectorize_and_persist_processor import process_vectorization_queue
from qa_syncup.sync_up_qa_articles_to_confluence import sync_up_interactions_to_confluence
from slack.channel_interaction import load_slack_bot
5


def add_space():
    retrieved_page_ids = get_space_content()
    indexed_page_ids = add_to_vector()
    return retrieved_page_ids, indexed_page_ids


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
            space_key = get_space_content()
            space_key = get_page_content_using_queue(space_key)
            process_vectorization_queue(space_key)
            print("\nSpace retrieval and indexing complete.")

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