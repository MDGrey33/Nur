# ./oai_assistants/file_manager.py
class FileManager:
    """
        FileManager handles operations related to file management in the context of the GPT-4-Turbo-Assistant.
        It provides functionalities to create, list, and delete files within the assistant's environment.
        """
    def __init__(self, client):
        """
        Initializes the FileManager with a client to manage files.

        Parameters:
        client (OpenAI_Client): The client object used for file operations.
        """
        self.client = client.files

    def create(self, file_path, purpose):
        """
        Creates a new file in the assistant's environment.

        Parameters:
        file_path (str): The path to the file to be uploaded.
        purpose (str): The purpose of the file.

        Returns:
        str: The ID of the created file.
        """
        with open(file_path, 'rb') as file_object:
            response = self.client.create(file=file_object, purpose=purpose)
            return response.id

    def list(self):
        """
        Lists all files currently managed by the assistant.

        Returns:
        dict: A dictionary with file IDs as keys and file details (filename and purpose) as values.
        """
        files_data = self.client.list().data
        return {file.id: {"filename": file.filename, "purpose": file.purpose} for file in files_data}

    def delete(self, file_id):
        """
        Deletes a file based on its ID.

        Parameters:
        file_id (str): The ID of the file to be deleted.

        Returns:
        str: Confirmation message stating the file has been deleted.
        """
        self.client.delete(file_id)
        return f"File with ID {file_id} has been deleted."
