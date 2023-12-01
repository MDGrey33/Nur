#!/bin/bash

# Path to the SQLite database file
DATABASE_PATH="./database/confluence_data.db"

# SQL command to delete all records from the tables
SQL_COMMAND="DELETE FROM space_data; DELETE FROM page_data;"

# Execute the SQL command
sqlite3 $DATABASE_PATH "$SQL_COMMAND"

echo "Database contents cleared."
