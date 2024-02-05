# /Users/roland/code/Nur/configuration.py
import os


project_path = "/Users/roland/code/Nur"
# build file_system_path and database_path from project_path
file_system_path = project_path + "/content/file_system"
database_path = project_path + "/content/database"
vector_folder_path = database_path + "/confluence_page_vectors"
vector_chunk_folder_path = database_path + "/confluence_page_vectors"
sql_file_path = database_path + "/confluence_pages_sql.db"

# paths for queues
# queue for extracting ans storing page content from Confluence
persist_page_processing_queue_path = os.path.join(project_path, "content", "transactional", "confluence_page_processing_queue")
# queue for creating page vectors and storing them in chroma db
persist_page_vector_queue_path = os.path.join(project_path, "content", "transactional", "confluence_page_vector_queue")
# queue for slack messages
persist_question_queue_path = os.path.join(project_path, "content", "transactional", "slack_question_queue")
# queue for slack reactions
persist_feedback_queue_path = os.path.join(project_path, "content", "transactional", "slack_feedback_queue")
# queue for qna documents
persist_qna_document_queue_path = os.path.join(project_path, "content", "transactional", "qna_document_queue")




assistant_id = "asst_wgR4j28Hf6CZKhuT2r4qovI8"
assistant_id_with_rag = "asst_IPv0wtSLfiVavwP1qUqBAyVi"