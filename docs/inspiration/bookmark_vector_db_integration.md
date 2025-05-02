# Design Decision: Add Confluence Pages to Vector DB for Context Retrieval

## Context
To enable the Najm Assistant to retrieve newly created or updated Confluence pages as context, we need to ensure these pages are vectorized and stored in the vector database immediately after creation.

## Options Considered
1. Direct integration in the workflow handler (blocking)
2. Asynchronous background task (FastAPI BackgroundTasks)
3. Event-driven with message broker

## Decision
We chose to use FastAPI's BackgroundTasks to asynchronously vectorize and upsert the page into the vector DB after successful creation/update. This approach is non-blocking, easy to implement, and aligns with our async, stateless, and scalable architecture principles. It can be refactored to an event-driven model in the future if needed.

## Implementation
- After creating/updating a Confluence page, trigger a background task to:
  - Generate an embedding for the page content
  - Upsert the vector and metadata into the vector DB
- Use real embedding and vector DB clients (no mocks or hardcoding)
- Add error handling and logging

## Future Considerations
- If scale or reliability needs increase, migrate to an event-driven approach with a message broker and dedicated worker service. 