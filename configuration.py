# ./configuration.py
import logging
from pathlib import Path
import os


def get_project_root() -> str:
    """Get the project root directory as a string.

    Assumes this script is located in the project root.
    """
    # Get the directory of the current script
    project_root = Path(__file__).parent
    # Convert the Path object to a string and return it
    return str(project_root)


logging.basicConfig(level=logging.INFO)

project_path = get_project_root()
logging.log(logging.DEBUG, f"Project path: {project_path}")

# build file_system_path and database_path from project_path
file_system_path = project_path + "/content/file_system"
database_path = project_path + "/content/database"
vector_folder_path = database_path + "/confluence_page_vectors"
interactions_folder_path = database_path + "/confluence_interaction_vectors"
vector_chunk_folder_path = database_path + "/confluence_page_vectors"
sql_file_path = database_path + "/confluence_pages_sql.db"

# paths for queues
# queue for extracting ans storing page content from Confluence
persist_page_processing_queue_path = os.path.join(project_path, "content", "transactional", "confluence_page_processing_queue")
# queue for creating page vectors and storing them in chroma db
persist_page_vector_queue_path = os.path.join(project_path, "content", "transactional", "confluence_page_vector_queue")
# queue for slack messages
persist_message_queue_path = os.path.join(project_path, "content", "transactional", "slack_message_queue")
# queue for slack questions
persist_question_queue_path = os.path.join(project_path, "content", "transactional", "slack_question_queue")
# queue for slack reactions
persist_feedback_queue_path = os.path.join(project_path, "content", "transactional", "slack_feedback_queue")
# queue for qna documents
persist_qna_document_queue_path = os.path.join(project_path, "content", "transactional", "qna_document_queue")



# Assistant IDs
assistant_id_prod = "asst_wgR4j28Hf6CZKhuT2r4qovI8"
assistant_id_with_rag = "asst_IPv0wtSLfiVavwP1qUqBAyVi"
assistant_id_on_free_credit_account = "asst_RjPJlkVCfaHTLgalw9BXAuBi"
assistant_id = assistant_id_prod

# Model IDs
# Doesn't apply for assistants
# Assistants have as part of the assistant the model id
gpt_3t = ""
gpt_4t = "gpt-4-1106-preview"
model_id = gpt_4t

# Embedding model IDs
embedding_model_id_latest_large = "text-embedding-3-large"
embedding_model_id_latest_small = "text-embedding-3-small"
embedding_model_id_ada = "text-embedding-ada-002"
embedding_model_id = embedding_model_id_latest_large

# document count is recommended from 3 to 15 where 3 is minimum cost and 15 is maximum comprehensive answer
document_count = 2

# Refactor: Might want to store only string values here cause the modules are all pulling the environment variable
# Configuration for the Nur Services API
# get the values from the environment variables if available or use the default values
api_host = os.environ.get("NUR_API_HOST", "localhost")
api_port = os.environ.get("NUR_API_PORT, 8000")

# Name of the vector collection
vector_collection_name = "TopAssist"
interactions_collection_name = "interactions"