# /Users/roland/code/Nur/configuration.py

project_path = "/Users/roland/code/Nur"
# build file_system_path and database_path from project_path
file_system_path = project_path + "/content/file_system"
database_path = project_path + "/content/database"
vector_folder_path = database_path + "/confluence_page_vectors"
vector_chunk_folder_path = database_path + "/confluence_page_vectors"
sql_file_path = database_path + "/confluence_pages_sql.db"

# paths for queues
# queue for extracting ans storing page content from Confluence
persist_page_processing_queue_path = project_path + "/content/transactional/confluence_page_processing_queue"
# queue for creating page vectors and storing them in chroma db
persist_page_vector_queue_path = project_path + "/content/transactional/confluence_page_vector_queue"

# Slack Bot User ID
bot_user_id = "U069C17DCE5"
