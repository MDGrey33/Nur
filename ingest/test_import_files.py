import os
import json
from pathlib import Path
from ingest.database import create_table, add_or_update_page
from ingest.file_traversal import find_files
from ingest.pdf_handler import extract_text_from_pdf
from ingest.doc_handler import extract_text_from_docx
from ingest.html_handler import extract_text_from_html  # Import the new function

"""
This module handles the setup and testing of the import files functionality.
It includes functions to set up the test environment and to test the import files process.
"""

def test_import_files():
    create_table()
    content_dir = 'content/import/files'
    metadata_dir = 'content/import/metadata'
    extensions = ['pdf', 'docx', 'html']  # Add 'html' to the list of extensions
    files = find_files(content_dir, extensions)
    
    for file in files:
        metadata_file = os.path.join(metadata_dir, f"{file.stem}.json")
        if not os.path.exists(metadata_file):
            continue
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        file_id = metadata.get('id')
        if not file_id:
            continue
        
        if file.suffix == '.pdf':
            content = extract_text_from_pdf(file)
        elif file.suffix == '.docx':
            content = extract_text_from_docx(file)
        elif file.suffix == '.html':
            content = extract_text_from_html(file)
        
        add_or_update_page(file_id, content)
    
    print("Files imported successfully")

if __name__ == "__main__":
    test_import_files()