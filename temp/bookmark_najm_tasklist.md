# Tasklist: Integrate Najm Assistant for Bookmark-to-Confluence Workflow

## Tasks

- [x] 1. Add Najm assistant ID to config file next to Shams and Amar (clarified as Groupon assistant)
- [ ] 2. Refactor bookmark event handler to:
    - [x] a. Fetch the full conversation thread (all messages, in order)
    - [x] b. Concatenate all messages into a single string
    - [x] c. Send the conversation string to Najm assistant using OpenAI API (in new use case module)
    - [x] d. Parse the JSON response (Title, Body)
    - [x] e. Use Title and Body to create/update the Confluence page
    - [x] f. Mark conversation as posted in the database
- [x] 3. Create new module: use_cases/conversation_to_document.py with generate_document_from_conversation
- [x] 4. Implement and test generate_document_from_conversation
- [x] 5. Test the new workflow end-to-end
- [x] 6. Refactor Najm workflow to use async FastAPI endpoint (like question answering)
- [X] 7. Update bookmark handler to call the new endpoint asynchronously
- [X] 8. Update this tasklist as progress is made 
- [x] 9. Add created/updated Confluence page to vector DB for context retrieval by the bot 