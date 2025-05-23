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
chart_folder_path = project_path + "/content/charts"
interactions_folder_path = database_path + "/confluence_interaction_vectors"
vector_chunk_folder_path = database_path + "/confluence_page_vectors"
sql_file_path = database_path + "/confluence_pages_sql.db"

# paths for queues
# Refactor: check if the queues are still used if note remove those lines 
# queue for extracting and storing page content from Confluence
persist_page_processing_queue_path = os.path.join(
    project_path, "content", "transactional", "confluence_page_processing_queue"
)
# queue for creating page vectors and storing them in chroma db
persist_page_vector_queue_path = os.path.join(
    project_path, "content", "transactional", "confluence_page_vector_queue"
)


# Assistant IDs
# Create one assistant for Q&A and one for Quizzes in your open AI account with the configuration in ./documentation/prompts.md
# All possible assistant ids to chose from
qa_assistant_groupon_shams = "asst_47gs7vcUWtFv0AYmIn6U7eP5"
quizz_assistant_id_groupon_amar = "asst_kPz810EmoWUEbKYvSS0rGkqp"
# Najm assistant for conversation-to-confluence-page formatting (Groupon workspace)
conversation_to_confluence_id_groupon_najm = "asst_YejB21s02oTxJGCrP35AHoSn"
# Assistant variables to use in the code
qa_assistant_id = qa_assistant_groupon_shams
quizz_assistant_id = quizz_assistant_id_groupon_amar
conversation_to_confluence_id = conversation_to_confluence_id_groupon_najm

# Model IDs
# Doesn't apply for assistants
# Assistants have as part of the assistant the model id
gpt_3t = ""
gpt_4t = "gpt-4-turbo-preview"
model_id = gpt_4t

# Embedding model IDs
embedding_model_id_latest_large = "text-embedding-3-large"
embedding_model_id_latest_small = "text-embedding-3-small"
embedding_model_id_ada = "text-embedding-ada-002"
embedding_model_id = embedding_model_id_latest_large

# page retrieval for answering questions
# document count is recommended from 3 to 15 where 3 is minimum cost and 15 is maximum comprehensive answer
document_count = 20
# interaction retrieval for identifying knowledge gaps interaction_retrieval_count is recommended from 3 to 10 where
# 3 is minimum cost and 10 is maximum comprehensive list of questions
interaction_retrieval_count = 10

# Configuration for the Nur Services API
# get the values from the environment variables if available or use the default values
api_host = os.environ.get("NUR_API_HOST", "localhost")
api_port = os.environ.get("NUR_API_PORT", "8001")

# Name of the vector collections
pages_collection_name = "pages"
interactions_collection_name = "interactions"


# System Knowledge space name on Confluence
system_knowledge_space_private = "Nur Documentation"
system_confluence_knowledge_space = system_knowledge_space_private


# Knowledge gap recovery Slack channel ids
slack_channel_debug = "C06RLR5S049"
channel_id = slack_channel_debug

# === Centralized context/model limits ===
# Maximum number of characters for context passed to the model or assistant
MAX_CONTEXT_LENGTH = 500000
# Maximum number of tokens for model output (used in OpenAI API calls)
MODEL_MAX_TOKENS = 4095
