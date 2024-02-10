# Nur
The self actualizing documentation framework that heals its knowledge gaps as naturally as a ray of light
[Custom GPT to discuss the code base](https://chat.openai.com/g/g-zKBLXtfrD-shams-nur)
## Feature list
### Done:
#### Capabilities
- add a confluence space to the bots knowledge
- have a conversation with the bot based on the knowledge
#### features
- Up to 15 documents in context with every question
- Up to 15 documents added to context with follow-up questions



### Todo:
- Dockerize the Solution
- enable function calling for context retrieval
- Space management
  - setup last update date and schedule to update confluence space with log in db 
  - create new vector database nightly and on trigger from sql database
- Refactor
  - store embeds in database
  - move from event consumer to database model
    - is_message_processed_in_db, 
    - record_message_as_processed_in_db 
    - add_question_and_response_to_database
- add api for faster space learning
- integrate GPT-3 for fast summarization in generate_extended_context_query in event consumer assistants module
- add questions, answers and reactions (- enable confluence edit or new page recommendation)
- add credibility rating to database 
- trivia question collector 



## Setup
Still in forming phase
For now clone the repo
Familiarize yourself with the modules
````
git clone https://github.com/MDGrey33/Nur.git
````
Run setup script inside setup package.


## Usage
1. Add openai api key to credentials
2. Add confluence credentials to ./credentials
3. To listen to slack create slack app and add the credentials in ./credentials
4. Run with python the module main.py clone a space and run the slack bot
5. Go to slack, channel test and ask a question and the bot will reply
