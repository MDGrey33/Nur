# ./main.py
from confluence_integration.retrieve_space import choose_space
from vector.chroma import retrieve_relevant_documents
from open_ai.assistants.query_assistant_from_documents import query_assistant_with_context
from open_ai.chat.query_from_documents import query_gpt_4t_with_context
from slack.bot import load_slack_bot
from open_ai.assistants.openai_assistant import load_manage_assistants
from interactions.vectorize_and_store import vectorize_interactions_and_store_in_db
from vector.create_interaction_db import VectorInteractionManager
from interactions.identify_knowledge_gap import identify_knowledge_gaps
from space.manager import Space
from visualize.pages import load_confluence_pages_spacial_distribution

def load_new_documentation_space():
    space_key, space_name = choose_space()
    if space_key and space_name:
        space = Space()
        space.load_new(space_key, space_name)


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
        print("7. Identify knowledge gaps")
        print("8. Visualize Confluence Pages Spacial Distribution")
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
            vector_interaction_manager = VectorInteractionManager()
            vector_interaction_manager.add_to_vector()

        elif choice == "5":
            print("Starting Slack Bot Using Assistants and fast API...")
            # Run the FastAPI server
            input("Started the FastAPI server located at './api/endpoint' and Press Enter to continue.")
            # Start the Slack bot in the main thread
            load_slack_bot()
            print("Slack Bot is running in parallel processing mode.")

        elif choice == "6":
            load_manage_assistants()

        elif choice == "7":
            context = input("Enter the context you want to identifying knowledge gaps in\nex:(billing reminders): ")
            identify_knowledge_gaps(context)

        elif choice == "8":
            print("Starting 3D visualization process...")
            load_confluence_pages_spacial_distribution()

        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter 0, 1, 2, 3, 4, 5, 6 or 7.")


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