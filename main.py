from confluence_integration.retrieve_space import get_space_content
from vector.chroma import add_to_vector, retrieve_relevant_documents
from oai_assistants.query_assistant_from_documents import query_assistant_with_context
from gpt_4t.query_from_documents import query_gpt_4t_with_context
from slack.channel_reaction import load_slack_bot


def add_space():
    retrieved_page_ids = get_space_content()
    indexed_page_ids = add_to_vector()
    return retrieved_page_ids, indexed_page_ids


def answer_question_with_assistant(question):
    relevant_document_ids = retrieve_relevant_documents(question)
    response = query_assistant_with_context(question, relevant_document_ids)
    return response

def answer_question_with_gpt_4t(question):
    relevant_document_ids = retrieve_relevant_documents(question)
    response = query_gpt_4t_with_context(question, relevant_document_ids)
    return response

question1 = "Do we support payment matching in our solution? and if the payment is not matched do we already have a way to notify the client that they have a delayed payment?"

"""# add_space()
# print("#"*100 + "\nSpace retrieval and indexing complete\n" + "#"*100)
print("Question 1: " + question1)
answer = answer_question(question1)
# print("Answer: " + answer)
print(answer)
print("#"*100 + "\nQuestion 1 answered\n" + "#"*100)
"""


def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Load New Documentation Space")
        print("2. Ask a Question to Existing Documentation with Assistant")
        print("3. Ask a question to Existing Documentation with GPT-4T")
        print("4. Start Slack Bot")
        print("0. Cancel/Quit")
        choice = input("Enter your choice (0-3): ")

        if choice == "1":
            add_space()
            print("\nSpace retrieval and indexing complete.")
        elif choice == "2":
            question = ask_question()
            if question:
                answer = answer_question_with_assistant(question)
                print("\nAnswer:", answer)
        elif choice == "3":
            question = ask_question()
            if question:
                answer = answer_question_with_gpt_4t(question)
                print("\nAnswer:", answer)
        elif choice == "4":
            print("Starting Slack Bot...")
            load_slack_bot()
            print("Slack Bot is running.")
        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter 0, 1, 2, or 3.")


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