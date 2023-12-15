import sqlite3
from prettytable import PrettyTable
from configuration import sql_file_path


def display_page_data():
    """
    Display all records in the 'page_data' table of the SQLite database.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(sql_file_path)
    cursor = conn.cursor()

    # Retrieve all records from the 'page_data' table
    cursor.execute("SELECT * FROM page_data")
    records = cursor.fetchall()

    # Create a PrettyTable
    table = PrettyTable()
    table.field_names = ["ID", "Page ID", "Space Key", "Title", "Author", "Created Date", "Last Updated", "Content", "Comments", "Last Embedded"]

    for record in records:
        formatted_record = list(record)
        # Assuming createdDate, lastUpdated, and lastEmbedded are already in a readable string format
        formatted_record[7] = (formatted_record[7][:75] + '...') if formatted_record[7] and len(formatted_record[7]) > 75 else formatted_record[7]  # Content (truncated)

        table.add_row(formatted_record)

    # Close the SQLite connection
    conn.close()

    print(table)


if __name__ == "__main__":
    display_page_data()
