import os
import json
import sqlite3
import pytest
from pathlib import Path
from ingest.database import create_table, add_or_update_page, DATABASE_PATH
from ingest.file_traversal import find_files
from ingest.pdf_handler import extract_text_from_pdf
from ingest.doc_handler import extract_text_from_docx
from ingest.html_handler import extract_text_from_html
from endpoint.import_files import import_files

@pytest.fixture(scope="module")
def setup_environment():
    # Ensure the database file is removed before the test
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    
    # Create necessary directories
    os.makedirs('content/import/files', exist_ok=True)
    os.makedirs('content/import/metadata', exist_ok=True)
    
    # Create sample metadata files
    metadata_files = {
        'sample_pdf.json': {
            "id": "pdf_001",
            "title": "Sample PDF Document",
            "author": "Author Name"
        },
        'sample_docx.json': {
            "id": "docx_001",
            "title": "Sample DOCX Document",
            "author": "Author Name"
        },
        'sample_html.json': {
            "id": "html_001",
            "title": "Sample HTML Document",
            "author": "Author Name"
        }
    }
    
    for filename, content in metadata_files.items():
        with open(f'content/import/metadata/{filename}', 'w') as f:
            json.dump(content, f)
    
    # Create sample files
    with open('content/import/files/sample.pdf', 'w') as f:
        f.write('%PDF-1.4\n%âãÏÓ\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 1\n/Kids [3 0 R]\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n/Resources <<\n/Font <<\n/F1 5 0 R\n>>\n>>\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello, PDF World!) Tj\nET\nendstream\nendobj\n5 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000074 00000 n \n0000000121 00000 n \n0000000213 00000 n \n0000000270 00000 n \ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n327\n%%EOF')
    
    with open('content/import/files/sample.docx', 'w') as f:
        f.write('This is a sample DOCX file.')
    
    with open('content/import/files/sample.html', 'w') as f:
        f.write('<html><body><h1>Hello, HTML World!</h1><p>This is a sample HTML file.</p></body></html>')

    yield

    # Cleanup after tests
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    for filename in metadata_files.keys():
        os.remove(f'content/import/metadata/{filename}')
    os.remove('content/import/files/sample.pdf')
    os.remove('content/import/files/sample.docx')
    os.remove('content/import/files/sample.html')

def test_import_files(setup_environment):
    import_files()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pages')
    rows = cursor.fetchall()
    
    pdf_imported = False
    docx_imported = False
    html_imported = False
    
    if rows:
        for row in rows:
            content = row[1]
            if content is not None:
                if row[0].startswith('pdf_'):
                    pdf_imported = True
                elif row[0].startswith('docx_'):
                    docx_imported = True
                elif row[0].startswith('html_'):
                    html_imported = True
    
    conn.close()
    
    assert pdf_imported, "PDF file was not imported successfully."
    assert docx_imported, "DOCX file was not imported successfully."
    assert html_imported, "HTML file was not imported successfully."
    print("All file types imported successfully.")