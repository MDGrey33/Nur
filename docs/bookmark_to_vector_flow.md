# :bookmark: Event to Vector DB Flow Documentation

## Overview
This document details the end-to-end process that occurs when a :bookmark: reaction is added in Slack, tracing the flow through the system, including all relevant file paths, databases, and vector DBs.

---

## 1. Project Structure and Key Paths

| Purpose | Variable | Path (relative to project root) |
|---------|----------|---------------------------------|
| **Main SQL DB** (Confluence pages, embeddings, etc.) | `sql_file_path` | `content/database/confluence_pages_sql.db` |
| **Vector DB (Chroma, persistent client)** | `vector_folder_path` | `content/database/confluence_page_vectors` |
| **Vector Chunks** | `vector_chunk_folder_path` | `content/database/confluence_page_vectors` |
| **Interaction Vectors** | `interactions_folder_path` | `content/database/confluence_interaction_vectors` |
| **File System Storage** | `file_system_path` | `content/file_system` |
| **Charts** | `chart_folder_path` | `content/charts` |

---

## 2. End-to-End :bookmark: Event Flow

### Step-by-Step Sequence

1. **Slack User adds :bookmark: reaction**
   - **File:** `slack/bot.py`, `slack/channel_message_handler.py`
   - **Handler:** `ChannelMessageHandler.handle` detects the event and calls `process_bookmark_added_event`.

2. **Process :bookmark: Event**
   - **File:** `slack/reaction_manager.py`
   - Fetches the conversation thread and POSTs it to `/api/v1/bookmark_to_confluence`.

3. **API Receives and Processes Event**
   - **File:** `api/endpoint.py`
   - Generates a document from the conversation, stores it in the DB, creates a Confluence page, and schedules vectorization.

4. **Bookmarked Conversation Storage**
   - **File:** `database/bookmarked_conversation_manager.py`
   - **DB Table:** `bookmarked_conversations` in `content/database/confluence_pages_sql.db`

5. **Confluence Page Storage**
   - **File:** `confluence_integration/store_page_local.py`
   - **Local Copy:** `content/file_system`
   - **DB Table:** `page_data` in `content/database/confluence_pages_sql.db`

6. **Vectorization and Storage**
   - **File:** `use_cases/vectorize_page.py`, `database/page_manager.py`
   - **Vector DB Path:** `content/database/confluence_page_vectors`
   - **DB Table:** `page_data.embed` (embedding stored as JSON string)

---

## 3. Mermaid Diagram

```mermaid
sequenceDiagram
    participant SlackUser as Slack User
    participant SlackBot as slack/bot.py
    participant ChannelHandler as slack/channel_message_handler.py
    participant ReactionMgr as slack/reaction_manager.py
    participant FastAPI as api/endpoint.py
    participant DocGen as use_cases/conversation_to_document.py
    participant BookmarkDB as database/bookmarked_conversation_manager.py
    participant Confluence as confluence_integration/system_knowledge_manager.py
    participant LocalStore as confluence_integration/store_page_local.py
    participant Vectorize as use_cases/vectorize_page.py
    participant VectorDB as database/page_manager.py

    SlackUser->>SlackBot: Adds :bookmark: reaction
    SlackBot->>ChannelHandler: Receives event
    ChannelHandler->>ReactionMgr: Calls process_bookmark_added_event
    ReactionMgr->>ReactionMgr: Fetches conversation thread
    ReactionMgr->>FastAPI: POST /api/v1/bookmark_to_confluence
    FastAPI->>DocGen: generate_document_from_conversation
    DocGen-->>FastAPI: Returns {title, body}
    FastAPI->>BookmarkDB: add_bookmarked_conversation<br/>(content/database/confluence_pages_sql.db)
    FastAPI->>Confluence: create_page_on_confluence<br/>(Nur Documentation)
    FastAPI->>BookmarkDB: update_posted_on_confluence
    FastAPI->>Confluence: get_page_id_by_title
    FastAPI->>LocalStore: store_page_locally_from_confluence<br/>(content/file_system)
    FastAPI->>Vectorize: background_tasks.add_task(vectorize_and_store_page)
    Vectorize->>VectorDB: add_or_update_embed_vector<br/>(content/database/confluence_page_vectors, page_data.embed)
    VectorDB-->>Vectorize: Embedding stored in DB

    Note over FastAPI,Vectorize: All DBs and vector stores are under content/database/
```

---

## 4. Potential Failure Points

- Slack event not triggered or not handled
- No messages fetched for the thread
- API call to `/api/v1/bookmark_to_confluence` fails
- Document generation or DB write fails
- Confluence page or vectorization fails
- Background task fails silently (embedding not written)

---

## 5. References
- All configuration values are set in `configuration.py`.
- All DBs and vector DBs are under `content/database/` relative to the project root.
- Local Confluence page copies are under `content/file_system`.

---

**For troubleshooting, check logs and DB entries at each step and verify the presence of files and embeddings at the specified paths.** 