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

Easy onboarding, reach out if you need support.

## Team
- [Roland Younes](https://www.linkedin.com/in/rolanday/) 
24 years in tech, 10 years in tech management 
and software development, 
2 years of healthy obsession in Gen AI and python
- You...? 
text me if you would like a walkthrough,
request a feature,
create an issue or make a pull request.

## Feature list

### Done:
#### Capabilities
- Learns from your confluence
- Chats with you in slack based on the knowledge in confluence
- Identifies knowledge gaps
- Asks questions on Slack to collect knowledge
- Capture :checkmark: reaction
- Summarise the conversation and add document to confluence
- gamification (leader board)
    - light seekers ( people who ask questions)
    - revealers ( people who ask undocumented questions)
    - luminaries ( people who contribute to knowledge gathering)
- visualize documentation in 3D space

### Todo:

- Space management
  - Retrieve documentation updates nightly
  - Delete documentation scope (Space) from vector

- Advanced Knowledge gap recovery gamification
  - Collects the top unanswered questions by theme
  - Identify the people who asked them
  - We invite to the Trivia channel the users who asked the. questions and the domain experts
  - The bot asks the questions, people answer and discuss till satisfaction
  - People thumbs up the good contributions
  - The bot collects the conversation data and based on it:
  - Proposes new documents
  - Upgrades the leaderboard with the top contributors

- Refactor
  - Move everything network to a network package
    - organize network functions into objects

- Enable function calling for context retrieval

- Build an algorythm that uses AI to manage retrieval cleanup and volume optimization locally

- Chunk to embed and context and providing document ids from metadata but keep including full documents in context

- Add credibility rating to database



## Setup
### prerequisites:
- sqlite3
- Python 3.12
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

`poetry run python ./main.py` (for the menu operations)

`poetry run python ./api/endpoint.py` (API / uvicorn web server)

Refer to the ./documentation/slack_app_manifest_installation_guide.md for slack bot setup

`poetry run python ./slack/bot.py` (slack bot stream listener)

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

## Technologies
- chromadb
- slack
- confluence
- persis-queue
## Technologies in consideration
- aws
- azure
- pinocone
- celery
- rabbitmq
- postgreaql


Refer to the ./documentation folder for project documentation.