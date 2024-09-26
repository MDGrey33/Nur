import sqlite3
from endpoint.import_files import import_files

def check_import():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pages')
    rows = cursor.fetchall()
    
    pdf_imported = False
    docx_imported = False
    html_imported = False
    
    if rows:
        print("Imported files:")
        for row in rows:
            content = row[1]
            if content is not None:
                print(f"ID: {row[0]}, Content:\n{content[:500]}...")  # Print first 500 characters of content
                print("\n--- End of Content Preview ---\n")
                if row[0].startswith('pdf_'):
                    pdf_imported = True
                elif row[0].startswith('docx_'):
                    docx_imported = True
                elif row[0].startswith('html_'):
                    html_imported = True
            else:
                print(f"ID: {row[0]}, Content: None")
    else:
        print("No files were imported.")
    
    conn.close()
    
    assert pdf_imported, "PDF file was not imported successfully."
    assert docx_imported, "DOCX file was not imported successfully."
    assert html_imported, "HTML file was not imported successfully."
    print("All file types imported successfully.")

if __name__ == "__main__":
    # Trigger the import process
    import_files()
    
    # Check the import results
    check_import()