# Nur
The self actualizing documentation framework that heals its knowledge gaps as naturally as a ray of light
[Custom GPT to discuss the code base](https://chat.openai.com/g/g-zKBLXtfrD-shams-nur)
## Feature list
### announcements:
- 2024-02-16: Migrated successfully to python 3.12 and poetry to simplify onboarding contributors
### Done:
#### Capabilities
- add a confluence space to the bots knowledge
- have a conversation with the bot based on the knowledge in any slack channel
#### features
- Up to 15 documents in context with every question
- Up to 15 documents added to context with follow-up questions

### Todo:
- Enable function calling for context retrieval
- Space management
  - create new vector database nightly and on trigger from sql database
- Refactor
  - store embeds in database
  - move from event consumer to database model
    - is_message_processed_in_db, 
    - record_message_as_processed_in_db 
    - add_question_and_response_to_database
- integrate GPT-3 for fast summarization in generate_extended_context_query in event consumer assistants module
- add questions, answers and reactions (- enable confluence edit or new page recommendation)
- add credibility rating to database 
- trivia question collector to generate new knowledge



## Setup
### prerequisites:
- python 3.12
- poetry
- pycharm
### Launching the app

````
git clone https://github.com/MDGrey33/Nur.git
cd Nur
poetry install
poetry run python main.py
````
open the project on pycharm you will be able to run:

./main.py (for the menu operations)

./api/endpoint.py (API / uvicorn web server)

./slack/channel_interaction_assistants.py (slack bot stream listener)

## Usage
1. Rename credentials_example.py to credentials.py
2. Add openai api key to ./credentials
2. Add confluence credentials to ./credentials
3. To listen to slack create slack app and add the credentials in ./credentials
4. All the operational content is in ./content you might want to chnage the path in configuration if running on docker.