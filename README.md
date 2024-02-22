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
- sqlite3
- python 3.12
- poetry
- pycharm

## Configuration
1. Rename credentials_example.py to credentials.py & .env.example to .env
2. Follow the instructions in the files to fill in the values


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

`nur-web` and `nur-slack` should be fully operational already. If you wish to run commands in Nur's cli interface, you will need to attach a shell to the `nur-manager` container in interactive mode, and enter the management environment:

```
./bin/manage
```

If the above works, you should see Nur's manager command prompt - the same thing you should see when running `./main.py` locally.

Bear in mind that the Dockerized version uses a shared volume named `nur_shared_content`. This is bootstrapped during the first installation, but will persist until it is manually removed.

## Network traffic

1. Outgoing to Open AI API (for Embeds and completion)
2. Two-way to slack api and from slack stream (for receiving and sending messages)
3. Outgoing anonymized telemetry data to Chroma that will be disabled soon
4. Outgoing to confluence API for (document management)
