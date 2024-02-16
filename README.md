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
- sqlite3
- python 3.12
- poetry
- pycharm

## Configuration
1. Rename credentials_example.py to credentials.py
2. Add openai api key to ./credentials
2. Add confluence credentials to ./credentials
3. To listen to slack create slack app and add the credentials in ./credentials
4. All operational content lives in `./content` in shell mode. This is shared as a volume when run via Docker.

### Run Nur via shell

````
git clone https://github.com/MDGrey33/Nur.git
cd Nur
poetry install
poetry run python main.py
````
open the project on pycharm you will be able to run:

`./main.py` (for the menu operations)

`./api/endpoint.py` (API / uvicorn web server)

`./slack/channel_interaction.py` (slack bot stream listener)

### Run Nur via Docker

We will use docker compose to build 3 containers of Nur. Each one is used to run a separate part of the app:
* `nur-manager` will create a container allowing us to use `main.py` functionality. It is meant to be interactive (read further for details).
* `nur-web` starts the web application.
* `nur-slack` starts the slack integration script.

First off, run the composer script:
```
git clone https://github.com/MDGrey33/Nur.git
cd Nur
docker composer up
```

Upon successful completion, you have three containers running, all of them sharing a common volume mounted at `/content` within the containers.

`nur-web` and `nur-slack` should be fully operational already. If you wish to run commands in Nur's cli interfact, you will need start the `nur-manager` container in interactive mode, and enter the management environment:

```
./bin/run
``` 

## Network traffic

1. Outgoing to Open AI API (for Embeds and completion)
2. Two-way to slack api and from slack stream (for receiving and sending messages)
3. Outgoing anonymized telemetry data to Chroma that will be disabled soon
4. Outgoing to confluence API for (document management)
