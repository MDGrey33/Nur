import sqlite3
from prettytable import PrettyTable
from configuration import sql_file_path


def display_space_data():
    """
    Display all records in the "space_data" table of the SQLite database.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(sql_file_path)
    cursor = conn.cursor()

    # Retrieve all records from the "space_data" table
    cursor.execute("SELECT * FROM space_data")
    records = cursor.fetchall()

    # Create a PrettyTable
    table = PrettyTable()
    table.field_names = ["ID", "Space Key", "URL", "Login", "Token"]

    for record in records:
        table.add_row(record)

    # Close the SQLite connection
    conn.close()

    print(table)


if __name__ == "__main__":
    display_space_data()
