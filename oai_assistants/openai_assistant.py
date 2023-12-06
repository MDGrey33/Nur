# ./oai_assistants/openai_assistant.py
from oai_assistants.utility import new_assistant, select_file_for_upload, initiate_client
from oai_assistants.file_manager import FileManager
from oai_assistants.assistant_manager import AssistantManager
from oai_assistants.thread_manager import ThreadManager


def create_assistant(client, new_assistant=new_assistant):
    """
    Creates a new assistant based on the provided template.

    Parameters:
    client: OpenAI client instance used for assistant creation.
    new_assistant (dict, optional): Template for the new assistant. Defaults to the global `new_assistant`.

    Returns:
    Assistant: An instance of the created assistant.
    """
    assistant_manager = AssistantManager(client)
    return assistant_manager.create_assistant(
        new_assistant['model'],
        new_assistant['name'],
        new_assistant['instructions'],
        new_assistant['tools'],
        new_assistant['description']
    )


def chat_with_assistant(thread_manager):
    """
    Facilitates a chat interaction with an assistant using the provided thread manager.

    Parameters:
    thread_manager (ThreadManager): An instance of ThreadManager to handle the chat thread.

    Returns:
    None
    """
    print("Welcome to the Assistant Chat!")
    thread_manager.create_thread()

    while True:  # Main chat loop
        message_files = []

        # File upload loop
        while True:
            action = input("1. Add a file\n2. Continue to add your message\nChoose an option: ")
            if action == "1":
                file_id = chose_and_upload_file(client, file_path='context_update')
                if file_id is not None:
                    message_files.append(file_id)
                    print(f"File uploaded successfully with ID: {file_id}")
                else:
                    print(
                        "File upload failed or was canceled. Please try again or choose to continue without a file.")
            elif action == "2":
                break
            else:
                print("Invalid option. Please choose 1 or 2.")

        # Message input loop
        user_message = ""
        print("You: \nWrite your message, or write 'QUIT' to abort the chat.")
        while True:
            user_input = input()
            if user_input.lower() == 'quit':
                print("Exiting chat.")
                return  # Exit the entire chat function
            else:
                user_message += user_input + "\n"
                if user_input.lower() == 'done':
                    break

        if user_message.strip():
            thread_manager.add_message_and_wait_for_reply(user_message, message_files)
        else:
            print("No message entered.")

        # After processing, continue the main chat loop
        print("\nContinue chatting, or type 'QUIT' to exit.")


def chose_and_upload_file(client, file_path='context_update'):
    """
    Allows the user to select and upload a file from the specified path.

    Parameters:
    client: OpenAI client instance used for file operations.
    file_path (str, optional): The path where files are located. Defaults to 'context_update'.

    Returns:
    str: The ID of the uploaded file, or None if the operation is unsuccessful or canceled.
    """
    file_manager = FileManager(client)
    chosen_file_path = select_file_for_upload(file_path)
    if chosen_file_path:
        print("Select the purpose of the file:")
        print("1. Fine-tune")
        print("2. Assistants")
        print("3. Fine-tune results")
        print("4. Assistants output")
        purpose_choice = input("Enter the number for the purpose (1, 2, 3 or 4):")
        if purpose_choice == "1":
            purpose = "fine-tune"
        elif purpose_choice == "2":
            purpose = "assistants"
        elif purpose_choice == "3":
            purpose = "fine-tune-results"
        elif purpose_choice == "4":
            purpose = "assistants_output"
        else:
            print("Invalid option.")
            return
        file_id = file_manager.create(chosen_file_path, purpose)
        print(f"File uploaded successfully with ID: {file_id}")
        return file_id


def add_file_to_assistant(assistant_manager, assistant_id):
    """
    Adds a file to the specified assistant.

    Parameters:
    assistant_manager (AssistantManager): An instance of AssistantManager to handle file addition.
    assistant_id (str): The ID of the assistant to add the file to.

    Returns:
    None
    """
    file_manager = FileManager(client)
    files = file_manager.list()

    print("Available Files:")
    file_list = list(files.items())
    for index, (file_id, file_data) in enumerate(file_list, start=1):
        print(f"{index}. {file_data['filename']} (ID: {file_id})")

    file_index = input("Select the number of the file you want to add or '0' to cancel: ")
    if file_index == '0':
        print("Operation canceled.")
        return

    try:
        file_index = int(file_index) - 1
        if 0 <= file_index < len(file_list):
            file_id_to_add = file_list[file_index][0]
            assistant_manager.add_file_to_assistant(assistant_id, file_id_to_add)
            print("File added successfully.")
            assistant_manager.print_assistant_details(assistant_id)
        else:
            print("Invalid file number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def chose_assistant(assistant_manager, assistants):
    """
    Allows the user to select an assistant from a list.

    Parameters:
    assistant_manager (AssistantManager): An instance of AssistantManager for managing assistants.
    assistants (list): A list of available assistants.

    Returns:
    str: The ID of the selected assistant, or None if the operation is canceled.
    """
    print("\nSelect an Assistant")
    print("-------------------")
    for index, assistant in enumerate(assistants, start=1):
        print(f"{index}. {assistant.name} (ID: {assistant.id})")
    print("0. Cancel - Return to the previous menu.")
    print("-------------------")

    assistant_index = input("Enter the number of the assistant you want to manage or '0' to cancel: ")
    if assistant_index == '0':
        print("Operation canceled.")
        return None

    try:
        assistant_index = int(assistant_index) - 1
        if 0 <= assistant_index < len(assistants):
            selected_assistant = assistants[assistant_index]
            assistant_id = selected_assistant.id
            assistant_manager.print_assistant_details(assistant_id)
            return assistant_id
        else:
            print("Invalid assistant number.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None


def chose_assistant_action():
    """
    Presents a menu for the user to choose an action to perform on an assistant.

    Returns:
    str: The selected action as a string.
    """
    print("\nChoose an Action for the Assistant")
    print("------------------------------------")
    print("1. Chat - Chat with this assistant.")
    print("2. Add File - Add a file to this assistant.")
    print("3. Update - Update this assistant's parameters.")
    print("4. Delete - Delete this assistant.")
    print("5. Check Files - Cleanup assistant files that are not available.")
    print("0. Cancel - Return to the previous menu.")
    print("------------------------------------")
    action = input("Choose an option (0-5): ")
    return action


def manage_assistants(client):
    """
    Provides a management interface for assistants.

    Parameters:
    client: OpenAI client instance used for managing assistants.

    Returns:
    None
    """
    assistant_manager = AssistantManager(client)
    assistants = assistant_manager.list_assistants().data

    if not assistants:
        print("No assistants available.")
        return

    assistant_id = chose_assistant(assistant_manager, assistants)

    if assistant_id is None:
        return

    action = chose_assistant_action()
    if action == '1':
        # Chat with assistant
        thread_manager = ThreadManager(client, assistant_id)
        chat_with_assistant(thread_manager)
    elif action == '2':
        # Add file to assistant
        assistant_manager.clean_missing_files_from_assistant(assistant_id)
        add_file_to_assistant(assistant_manager, assistant_id)
    elif action == '3':
        # Update assistant parameters
        # Call the interactive update method from AssistantManager
        assistant_manager.clean_missing_files_from_assistant(assistant_id)
        assistant_manager.update_assistant_interactively(assistant_id)
        print("Assistant updated successfully.")
    elif action == '4':
        # Delete the assistant
        delete_message = assistant_manager.delete_assistant(assistant_id)
        print(delete_message)
    elif action == '5':
        assistant_manager.clean_missing_files_from_assistant(assistant_id)
    elif action == '6':
        # exit menu
        print("Operation canceled.")
    else:
        print("Invalid action.")


def manage_files(client):
    """
    Provides a file management interface for managing files associated with assistants.

    Parameters:
    client: OpenAI client instance used for file management.

    Returns:
    None
    """
    file_manager = FileManager(client)

    while True:
        files = file_manager.list()
        print("\nFile Management Menu")
        print("----------------------")
        print("1. List Files - Display available files.")
        print("2. Delete File - Remove a specific file.")
        print("3. Upload File - Add a new file.")
        print("0. Cancel - Return to the previous menu.")
        print("----------------------")

        choice = input("Select an option (0-3): ")

        if choice == '1':
            print("Available Files:")
            for file_id, file_data in files.items():
                print(f"ID: {file_id}, Filename: {file_data['filename']}, Purpose: {file_data['purpose']}")
        elif choice == '2':
            if not files:
                print("No files available to delete.")
                continue

            print("Select the file to delete:")
            file_list = list(files.items())
            for index, (file_id, file_data) in enumerate(file_list, start=1):
                print(f"{index}. {file_data['filename']} (ID: {file_id})")

            file_index = input("Enter the number of the file you want to delete or '0' to cancel: ")
            if file_index == '0':
                continue

            try:
                file_index = int(file_index) - 1
                if 0 <= file_index < len(file_list):
                    file_id_to_delete = file_list[file_index][0]
                    status = file_manager.delete(file_id_to_delete)
                    print(f"File deleted: {status}")
                else:
                    print("Invalid file number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == '3':
            file_id = chose_and_upload_file(client)
            print(f"File uploaded: ID {file_id}")
        elif choice == '0':
            print("Exiting File Management Menu.")
            break
        else:
            print("Invalid option. Please select a valid number.")


def user_interaction(client):
    """
    Provides the main user interaction interface for managing files and assistants.

    Parameters:
    client: OpenAI client instance used for user interactions.

    Returns:
    None
    """
    while True:
        print("\nUser Interaction Menu:")
        print("--------------------------------")
        print("1. Manage Files - Handle file-related operations.")
        print("2. Manage Assistants - View, modify, or delete assistants.")
        print("3. Create a New Assistant - Start the process of creating a new assistant.")
        print("0. Exit - Exit the user interaction menu.")
        print("--------------------------------")

        choice = input("Enter your choice (0-3): ")
        if choice == '1':
            manage_files(client)
        elif choice == '2':
            manage_assistants(client)
        elif choice == '3':
            created_assistant = create_assistant(client, new_assistant)
            print(f"New assistant created with ID: {created_assistant.id}")
        elif choice == '0':
            print("Exiting user interaction menu.")
            break
        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    client = initiate_client()
    user_interaction(client)
