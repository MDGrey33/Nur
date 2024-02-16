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
- Refactor 
  - Move everything database to the database package
    - organize database functions into objects
  - Move everything network to a network package
    - organize network functions into objects
  - Move everything file related to a file package
    - organize file functions into objects
- Space management
  - Retrieve documentation updates nightly
  - Delete documentation scope (Space) from vector
- Enable function calling for context retrieval
- Build an algorythm that uses AI to manage retrieval cleanup and volume optimization locally
- Add interaction to confluence space 
- Enable confluence edit or new page recommendation
- Add credibility rating to database 
- Trivia question collector to recover knowledge gaps



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
3. Add confluence credentials to ./credentials
4. To listen to slack create slack app and add the credentials in ./credentials
5. All the operational content is in ./content you might want to chnage the path in configuration if running on docker.

## Network traffic

1. Outgoing to Open AI API (for Embeds and completion)
2. Two-way to slack api and from slack stream (for receiving and sending messages)
3. Outgoing anonymized telemetry data to Chroma that will be disabled soon
4. Outgoing to confluence API for (document management)
