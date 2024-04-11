# ./configuration.py
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



project_path = get_project_root()

# build file_system_path and database_path from project_path
logging_path = project_path + "/content/logging"
file_system_path = project_path + "/content/file_system"
database_path = project_path + "/content/database"
vector_folder_path = database_path + "/confluence_page_vectors"
chart_folder_path = project_path + "/content/charts"
interactions_folder_path = database_path + "/confluence_interaction_vectors"
vector_chunk_folder_path = database_path + "/confluence_page_vectors"
sql_file_path = database_path + "/confluence_pages_sql.db"


# Assistant IDs
qa_assistant_id_prod_shams = "asst_wgR4j28Hf6CZKhuT2r4qovI8"
qa_assistant_id_with_rag_shams = "asst_IPv0wtSLfiVavwP1qUqBAyVi"
qa_assistant_personal = "asst_XGN0sfllK35yGC1TUb5n9BEZ"
quizz_assistant_id_amar = "asst_nMlrzxoYSepkH0AigAtRDMdl"
qa_assistant_id_on_free_credit_account = "asst_RjPJlkVCfaHTLgalw9BXAuBi"
quizz_assistant_id_personal = "asst_DQv5SrdFO1atzNB5PA5sd1nH"
qa_assistant_id = qa_assistant_personal
quizz_assistant_id = quizz_assistant_id_personal

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

# page retrieval for answering questions
# document count is recommended from 3 to 15 where 3 is minimum cost and 15 is maximum comprehensive answer
document_count = 2
# interaction retrieval for identifying knowledge gaps interaction_retrieval_count is recommended from 3 to 10 where
# 3 is minimum cost and 10 is maximum comprehensive list of questions
interaction_retrieval_count = 5

# Configuration for the Nur Services API
# get the values from the environment variables if available or use the default values
api_host = os.environ.get("NUR_API_HOST", "localhost")
api_port = os.environ.get("NUR_API_PORT", "8000")

# Name of the vector collection
pages_collection_name = "pages"
interactions_collection_name = "interactions"


# System Knowledge space name on Confluence
system_knowledge_space_private = "Nur Documentation"
system_confluence_knowledge_space = system_knowledge_space_private


# Knowledge collection Slack channel ids
slack_channel_priv_kb = "C06EGCDNA4A"
slack_channel_tt_ta_debug = "C06EA5WFGUF"
slack_channel_tt_ta = "C052GJ7GLVC"
slack_channel_debug = "C06RLR5S049"
channel_id = slack_channel_debug
