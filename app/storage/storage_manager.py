import os

class StorageManager:
    def create_file(self, file_identifier, content):
        storage_folder = "./app/storage"
        confluence_folder = os.path.join(storage_folder, "confluence")

        # Create the storage folder if it doesn't exist
        if not os.path.exists(storage_folder):
            os.makedirs(storage_folder)

        # Create the confluence folder if it doesn't exist
        if not os.path.exists(confluence_folder):
            os.makedirs(confluence_folder)

        # Define the path to the test.txt file inside the confluence folder
        test_file_path = os.path.join(confluence_folder, file_identifier + ".txt")

        # Create the test.txt file
        with open(test_file_path, "w") as file:
            file.write(content)