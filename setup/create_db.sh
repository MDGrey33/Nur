#!/bin/bash

# File name for the SQLite database
DB_FILE="confluence_data.db"

# SQL commands to create tables
SQL="
CREATE TABLE IF NOT EXISTS space_data (
    space_name TEXT,
    url TEXT,
    login TEXT,
    token TEXT
);

CREATE TABLE IF NOT EXISTS pages_data (
    page_id INTEGER PRIMARY KEY,
    space_key TEXT,
    title TEXT,
    content TEXT,
    author TEXT,
    created_date TEXT,
    last_updated TEXT,
    comments TEXT
);
"

# Execute SQL commands using SQLite
sqlite3 $DB_FILE "$SQL"
