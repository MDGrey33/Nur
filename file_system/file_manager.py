# ./file_system/file_manager.py
import os
from configuration import file_system_path

"""
A module to manage file system operations.
Creating files, deleting files, moving files, listing files in file_system_path directory.=
"""


class FileManager:
    """ Class to manage file system operations."""
    def __init__(self):
        self.file_system_path = file_system_path

    def create(self, file_name, file_content):
        """ Create a file in file_system_path directory."""
        with open(os.path.join(self.file_system_path, file_name), 'w') as file_object:
            file_object.write(file_content)
            return f"File {file_name} has been created."

    def delete(self, file_name):
        """ Delete a file in file_system_path directory."""
        os.remove(os.path.join(self.file_system_path, file_name))
        return f"File {file_name} has been deleted."

    def list(self):
        """ List all files in file_system_path directory."""
        return os.listdir(self.file_system_path)

    def add_content(self, file_name, file_content):
        """ Add a file in file_system_path directory."""
        with open(os.path.join(self.file_system_path, file_name), 'a') as file_object:
            file_object.write(file_content)
            return f"File {file_name} has been added."

    def read(self, file_name):
        """ Read a file in file_system_path directory."""
        with open(os.path.join(self.file_system_path, file_name), 'r') as file_object:
            return file_object.read()

