# Nur AI
The self-actualizing documentation Chat Bot that heals its knowledge gaps
as naturally as a ray of light - with AI
[Custom GPT to discuss the code base](https://chat.openai.com/g/g-zKBLXtfrD-shams-nur)

## Problem
Organizational knowledge is hard to find and keep updated.
 Accessing information is challenging for busy individuals or those with neuro-divergent brains.
 Current solutions lead to outdated documentation and inaccessible information.

## Solution
Nur AI utilizes generative AI to identify and fill knowledge gaps.
Offers both text and in the future audio access to documentation.
Currently in extensive MVP testing.

## Business model
Open Source free to use -
Apache-2 license
Notable solutions built as a subset of the Nur AI Functionality is Toptal's Top Assist https://github.com/toptal/top_assist

Easy onboarding, reach out if you need support.

## Team
- [Roland Younes](https://www.linkedin.com/in/rolanday/): With 24 years in tech, including 10 years in tech management and software development, Roland brings a wealth of experience alongside a 2-year deep dive into Gen AI and Python.

- You...? Interested in AI, documentation, and making a difference? Join us! Whether it’s for a chat, a feature request, or to contribute, we're open to your ideas and contributions.

## Feature list

### Done:
#### Capabilities
- Learns from your confluence
- Chats with you in slack based on the knowledge in confluence
- Identifies knowledge gaps
- Asks questions on Slack to collect knowledge
- Capture :checkmark: reaction
  - Summarise the conversation and add document to confluence
- Capture :bookmark: reaction
  - Add the conversation to confluence
- gamification (leader board)
    - light seekers ( people who ask questions)
    - revealers ( people who ask undocumented questions)
    - luminaries ( people who contribute to knowledge gathering)
- visualize documentation in 3D space

### Todo:
- Rewriting the full solution to scale
- Working in enhancing the onboarding process
- Modular branch shows the progress in standardizing the code with fast api

- Space management
  - Retrieve documentation updates nightly
  - Delete documentation scope (Space) from vector
  - Private chat with users after oauth on all spaces they have access to

- Enable function calling for context retrieval

- Build an algorythm that uses AI to manage retrieval cleanup and volume optimization locally

- Chunk to embed and context and providing document ids from metadata but keep including full documents in context

- Add credibility rating to database


## Setup
### prerequisites:
- sqlite3
- Python 3.12
- poetry


## Configuration
1. Rename credentials_example.py to credentials.py & .env.example to .env
2. Follow the instructions in the files to fill in the values
3. Follow the instructions in the configuration.py to add the relevant IDs
4. rename the .env.example to .env and update the values in the file

### Run Nur via shell

````
git clone https://github.com/MDGrey33/Nur.git
cd Nur
poetry install
poetry run python main.py
````

`poetry run python ./main.py` (for the menu operations)

`poetry run python ./api/endpoint.py` (API / uvicorn web server)

Refer to the ./documentation/slack_app_manifest_installation_guide.md for slack bot setup

`poetry run python ./slack/bot.py` (slack bot stream listener)

### Run Nur via Docker (experimental)

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

## Technologies
- Confluence (Data source)
- Slack (Chat service)
- OpenAI GPT4T (Text processing and generation)
- OpenAI Assistant (Chat management and context)
- OpenAI Embeds (Embed generation for text)
- ChromaDB (Vector db similarity search using embeds)
- SQLLite (local database for Documents and Interactions)
- FastAPI (API endpoint to run async and parallel processing)

## Technologies in consideration
- aws
- azure
- pinocone
- celery
- rabbitmq
- postgreaql
- Alembic

## Documentation
Refer to the ./documentation folder for project documentation.

## Test instruction
### preparation
Create a free confluence space and slack workspace.
More detail in the README.md though in brief:
Watch the video
Clone the repo
Create the slack app using the manifesto
Create an assistant on your open ai account
Create the credentials and configuration files
Launch the 3 scripts
Add some documentation on confluence
Load the space from the terminal
Invite the bot to slack
### Test scenarios:
1. ask question related to your documentation
2. ask questions not included in your documentation
3. have a conversation without a "?" in which you ask a question and then reply with the answer then bookmark it to add it to Nurs knowledge
4. ask a question related to the data you just bookmarked
5. from the terminal request a knowledge gap recovery
6. Answer the questions the bot asked on the channel and slect them as complete
7. monitor the points you got on the score board in the channel
