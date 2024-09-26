import os
from pathlib import Path

def find_files(directory, extensions):
    return [Path(os.path.join(root, file))
            for root, _, files in os.walk(directory)
            for file in files
            if file.split('.')[-1] in extensions]