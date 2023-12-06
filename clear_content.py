# doesnt work needs fixing

import os
import shutil
from configuration import file_system_path, database_path, vector_folder_path


def clear_directory(directory):
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


# Clearing directories
clear_directory(file_system_path)
clear_directory(database_path)
clear_directory(vector_folder_path)

print("Content of specified directories has been cleared.")
