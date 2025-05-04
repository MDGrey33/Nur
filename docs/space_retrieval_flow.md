# Space Retrieval and Embedding Flow

This document describes the end-to-end process for retrieving a Confluence space, extracting page data (including author and space key), and embedding that data for semantic search. This is the flow triggered by option 1 in `main.py` ("Load New Documentation Space").

---

## 1. User Action: Load New Documentation Space

- **File:** `main.py`
- **Code:**
  ```python
  if choice == "1":
      print("Loading new documentation space...")
      load_new_documentation_space()
  ```
- **Effect:** Calls `load_new_documentation_space()`.

---

## 2. Choose Space

- **File:** `confluence_integration/retrieve_space.py`
- **Code:**
  ```python
  def choose_space():
      confluence_client = ConfluenceClient()
      spaces = confluence_client.retrieve_space_list()
      ...
      return spaces[choice]["key"], spaces[choice]["name"]
  ```
- **Effect:** User selects a space from Confluence.

---

## 3. Load Space Content

- **File:** `space/manager.py`
- **Code:**
  ```python
  def load_new(self, space_key, space_name):
      ...
      get_space_content(space_key)
      get_page_content_using_queue(space_key)
      embed_pages_missing_embeds()
      ...
  ```
- **Effect:**
  - Enqueues all page IDs for processing
  - Processes each page
  - Embeds pages missing embeddings

---

## 4. Enqueue All Page IDs

- **File:** `confluence_integration/retrieve_space.py`
- **Code:**
  ```python
  def get_space_content(space_key, update_date=None):
      all_page_ids = get_all_page_ids_recursive(space_key)
      ...
      for page_id in all_page_ids:
          page_queue.put(page_id)
  ```
- **Effect:** All page IDs for the space are queued for processing.

---

## 5. Process Each Page

- **File:** `confluence_integration/extract_page_content_and_store_processor.py`
- **Code:**
  ```python
  def get_page_content_using_queue(space_key):
      ...
      while not page_queue.empty():
          page_id = page_queue.get()
          page_data = process_page(page_id, space_key, file_manager, page_content_map)
          if page_data:
              page_content_map[page_id] = page_data
      store_pages_data(space_key, page_content_map)
  ```
- **Effect:**
  - For each page, fetches and processes content and metadata.
  - Stores all page data in the database.

---

## 6. Extract Metadata and Write File

- **File:** `confluence_integration/retrieve_space.py`
- **Code:**
  ```python
  def process_page(page_id, space_key, file_manager, page_content_map):
      ...
      page = confluence.get_page_by_id(page_id, expand="body.storage,history,version")
      ...
      page_data = {
          "spaceKey": space_key,
          "pageId": page_id,
          "title": page_title,
          "author": page_author,
          ...
      }
      formatted_content = format_page_content_for_llm(page_data)
      file_manager.create(f"{page_id}.txt", formatted_content)
      ...
      return page_data
  ```
- **Effect:**
  - Extracts all metadata (including author and space key) from Confluence.
  - Writes a `.txt` file and adds the data to the in-memory map.

---

## 7. Store Page Data in Database

- **File:** `database/page_manager.py`
- **Code:**
  ```python
  def store_pages_data(space_key, pages_data):
      ...
      new_page = PageData(
          page_id=page_id,
          space_key=space_key,
          title=page_info["title"],
          author=page_info["author"],
          ...
      )
      session.add(new_page)
      ...
  ```
- **Effect:**
  - Stores all page data (including author and space key) in the database.

---

## 8. Embed Pages Missing Embeddings

- **File:** `confluence_integration/extract_page_content_and_store_processor.py`
- **Effect:**
  - Finds all pages missing embeddings and triggers embedding creation for them.

---

## 9. Embedding Logic

- **File:** `vector/chroma.py`
- **Code:**
  ```python
  def generate_document_embedding(page_id, model=embedding_model_id):
      ...
      author = page.author or ""
      space_key = page.space_key or ""
      title = page.title or ""
      content = page.content or ""
      embedding_text = f"Author: {author}\nSpace Key: {space_key}\nTitle: {title}\n{content}"
      embedding_json = embed_text(text=embedding_text, model=model)
      ...
  ```
- **Effect:**
  - Embedding is created from the author, space key, title, and content, all sourced from the database.

---

## Mermaid Diagram: Retrieve Space Flow

```mermaid
flowchart TD
    A[main.py: User chooses 'Load New Documentation Space'] --> B[load_new_documentation_space()]
    B --> C[choose_space(): User selects space]
    C --> D[Space().load_new(space_key, space_name)]
    D --> E[get_space_content(space_key)]
    E --> F[get_all_page_ids_recursive(space_key)]
    F --> G[Enqueue all page IDs for processing]
    D --> H[get_page_content_using_queue(space_key)]
    H --> I[For each page_id: process_page()]
    I --> J[Fetch page from Confluence]
    J --> K[Extract metadata (author, spaceKey, etc.)]
    K --> L[Write .txt file and add to page_content_map]
    H --> M[store_pages_data(space_key, page_content_map)]
    M --> N[Store all page data (author, space_key, etc.) in DB]
    D --> O[embed_pages_missing_embeds()]
    O --> P[For each page missing embed: generate_document_embedding()]
    P --> Q[Fetch author, space_key, title, content from DB]
    Q --> R[Create embedding: Author, Space Key, Title, Content]
    D --> S[space_manager.upsert_space_info(self)]
    D --> T[add_embeds_to_vector_db(space_key)]
```

---

## Notes
- The flow is robust as long as the Confluence data and the local schema are in sync.
- All metadata (including author and space key) is extracted from Confluence and included in both the database and the embedding.
- If you change the schema or add new metadata, ensure all steps in this flow are updated accordingly. 