# Context Length Management in Nur

## GPT-4.1 Context Window (Latest as of 2025)

- **Maximum context window:** 300,000 tokens (input + output combined)
- **Estimated max characters in one message:** ~1,200,000 (assuming 4 characters per token)
- **Max output tokens:**
  - 32,768 for o1-preview
  - 65,536 for o1-mini

**References:**
- [Why am I hitting 300,000 tokens limit on GPT4.1, which should have 1M context length? (OpenAI Community)](https://community.openai.com/t/why-am-i-hitting-300-000-tokens-limit-on-gpt4-1-which-should-have-1m-context-length/1249404)
- [What is the token context window size of the GPT-4 o1-preview model? (OpenAI Community)](https://community.openai.com/t/what-is-the-token-context-window-size-of-the-gpt-4-o1-preview-model/954321)
- [OpenAI Tokenizer Documentation](https://platform.openai.com/tokenizer)

| Model                | Max Context Window (tokens) | Max Output Tokens | Est. Max Characters (input+output) |
|----------------------|----------------------------|-------------------|-------------------------------------|
| gpt-4.1-preview      | 300,000                    | 32,768            | ~1,200,000                          |
| gpt-4.1-mini         | 300,000                    | 65,536            | ~1,200,000                          |

---

This document tracks all places in the codebase where the context provided to language models is measured, limited, or trimmed. It is intended as a living reference for developers to understand and extend context management practices.

---

## 1. `open_ai/assistants/query_assistant_from_documents.py`

### `format_pages_as_context`

This function explicitly measures and limits the context string to a maximum length (default: 300,000 tokens, see config). If adding more content would exceed the limit, it truncates the context and appends a notice.

```python
def format_pages_as_context(file_ids, max_length=MAX_CONTEXT_LENGTH):
    context = ""
    for file_id in file_ids:
        if len(context) >= max_length:
            break
        ...
        additional_context = (
            f"\nDocument Title: {title}\nSpace Key: {space_key}\n\n{file_content}"
        )

        if len(context) + len(additional_context) <= max_length:
            context += additional_context
        else:
            available_space = (
                max_length
                - len(context)
                - len(" [Content truncated due to size limit.]")
            )
            context += (
                additional_context[:available_space]
                + " [Content truncated due to size limit.]"
            )
            break

    return context
```

- **Purpose:** Prevents the context string from exceeding a set length before being sent to the model.
- **Location:** `open_ai/assistants/query_assistant_from_documents.py`

---

## 2. `open_ai/chat/query_from_documents.py`

### Model API Parameter (Not Code-side Trimming)

```python
response = client.chat.completions.create(
    ...
    max_tokens=MODEL_MAX_TOKENS,
    ...
)
```
- **Purpose:** Limits the model's output length, but does **not** trim the context string in code before sending.
- **Location:** `open_ai/chat/query_from_documents.py`

---

## 3. Other Files

As of this writing, no other files in the codebase (including `main.py`, `slack/event_consumer.py`, `slack/reaction_manager.py`, `use_cases/conversation_to_document.py`, or the utility/instruction files) contain code that measures, trims, or limits the context length before sending to the model.

---

## Usage of `format_pages_as_context`

Below are all the places in the codebase where `format_pages_as_context` is used, with code snippets and explanations:

### 1. `open_ai/chat/query_from_documents.py`

**Usage:**
```python
def query_gpt_4t_with_context(question, page_ids):
    ...
    context = format_pages_as_context(page_ids)
    ...
```
- **Purpose:** Formats the context from a list of file IDs before passing it to the model.
- **Location:** `open_ai/chat/query_from_documents.py`, line 107

---

### 2. `open_ai/assistants/query_assistant_from_documents.py`

**Usage:**
```python
def query_assistant_with_context(question, page_ids, thread_id=None):
    ...
    context = format_pages_as_context(page_ids)
    ...
```
- **Purpose:** Formats the context from a list of file IDs before sending it to the assistant.
- **Location:** `open_ai/assistants/query_assistant_from_documents.py`, line 122

---

### 3. `open_ai/assistants/query_assistant_rag_tool.py`

**Usage:**
```python
def query_assistant_with_context(question, page_ids, thread_id=None):
    ...
    context = format_pages_as_context(page_ids)
    ...
```
- **Purpose:** Formats the context from a list of file IDs before sending it to the assistant (RAG tool variant).
- **Location:** `open_ai/assistants/query_assistant_rag_tool.py`, line 124

---

### 4. `context/prepare_context.py`

**Usage:**
```python
def get_context(context_query, max_length=MAX_CONTEXT_LENGTH):
    ...
    documents = format_pages_as_context(context_document_ids, max_length)
    ...
```
- **Purpose:** Formats relevant documents as context for use in a JSON-compatible dictionary.
- **Location:** `context/prepare_context.py`, line 66

---

### Summary Table

| File/Function                                      | How `format_pages_as_context` Is Used                                                                 |
|----------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| `open_ai/chat/query_from_documents.py`<br>`query_gpt_4t_with_context` | Formats context from file IDs for model input.                                                         |
| `open_ai/assistants/query_assistant_from_documents.py`<br>`query_assistant_with_context` | Formats context from file IDs for assistant input.                                                     |
| `open_ai/assistants/query_assistant_rag_tool.py`<br>`query_assistant_with_context` | Formats context from file IDs for assistant input (RAG tool variant).                                  |
| `context/prepare_context.py`<br>`get_context`      | Formats relevant documents as context for use in a JSON-compatible dictionary.                         |

---

## Summary Table

| File/Function                                      | How Context Length Is Limited/Measured/Trimmed                                                                 |
|----------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| `open_ai/assistants/query_assistant_from_documents.py`<br>`format_pages_as_context` | Explicitly measures and trims context to a max length (default 300,000), truncates and appends a notice if needed. |
| `open_ai/chat/query_from_documents.py`<br>Model API call | Sets `max_tokens` for model output, but does **not** trim context in code.                                       |

---

## To Be Extended

This document is a living reference. Please add any new context management logic or related findings here as the codebase evolves. 