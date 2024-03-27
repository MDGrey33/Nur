# ./file_system/file_manager.py
import os
from configuration import file_system_path

# A module to manage file system operations.
# Includes functionalities for creating, deleting, adding to, and listing files in the file_system_path directory.
# The file_system_path directory is specified in the configuration.py file.


class FileManager:
    """
    Class to manage file system operations in a specified directory.

    Attributes:
    file_system_path (str): The path to the directory where file operations are performed.
    """

    def __init__(self):
        """
        Initializes the FileManager with a specific directory path.
        """
        self.file_system_path = file_system_path

    def create(self, file_name, file_content):
        """
        Create a file with specified content in the file system path.

        Args:
        file_name (str): The name of the file to be created.
        file_content (str): The content to be written to the file.

        Returns:
        str: Confirmation message that the file has been created.
        """
        with open(os.path.join(self.file_system_path, file_name), "w") as file_object:
            file_object.write(file_content)
            return f"File {file_name} has been created."

    def delete(self, file_name):
        """
        Delete a file from the file system path.

        Args:
        file_name (str): The name of the file to be deleted.

        Returns:
        str: Confirmation message that the file has been deleted.
        """
        os.remove(os.path.join(self.file_system_path, file_name))
        return f"File {file_name} has been deleted."

    def list(self):
        """
        List all files in the file system path directory.

        Returns:
        list: A list of file names in the directory.
        """
        return os.listdir(self.file_system_path)

    def add_content(self, file_name, file_content):
        """
        Add content to an existing file in the file system path.

        Args:
        file_name (str): The name of the file to be appended to.
        file_content (str): The content to be added to the file.

        Returns:
        str: Confirmation message that the file has been updated.
        """
        with open(os.path.join(self.file_system_path, file_name), "a") as file_object:
            file_object.write(file_content)
            return f"File {file_name} has been added."

    def read(self, file_name):
        """
        Read and return the content of a file in the file system path.

        Args:
        file_name (str): The name of the file to be read.

        Returns:
        str: The content of the file.
        """
        with open(os.path.join(self.file_system_path, file_name), "r") as file_object:
            return file_object.read()
