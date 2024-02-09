# Nur
The self actualizing documentation framework that heals its knowledge gaps as naturally as a ray of light
[Custom GPT to discuss the code base](https://chat.openai.com/g/g-zKBLXtfrD-shams-nur)
## Feature list
### Done:
- add a confluence space (url credentials and update interval) 
- Pulls the confluence space and stores it in a sqlite database
- Vectorizes the confluence space pages and stores the embeds in a chroma db collection
- Uses the vectorized embeds to find the most similar pages to a question
- Creates an assistant with the relevant pages and allows it to engage to provide the answer
- Listens on specific slack channels for questions relevant to its domain
- Implement fast response using Gpt-4 Turbo without assistant
- Implemented persist queue for page content retrieval and vectorization


### Todo:
- Dockerize the Solution
- Some messages from slack are skipped: 
  - considered async and now im more convinced the solution is to use API for paralellization and I will remove the file queues eventually
- Make a module that use assistants in the slack channel 
  - Assistants can now answer feedback questions
  - Need to enable context retrieval function calling by the assistant
- Space management
  - setup last update date and schedule to update confluence space with log in db
- Refactor
  - store embeds in database
  - move from event consumer to database model
    - is_message_processed_in_db, 
    - record_message_as_processed_in_db 
    - add_question_and_response_to_database
- integrate GPT-3 for fast summarization in generate_extended_context_query in event consumer assistants module
- create new vector database nightly and on trigger from sql database
- parallelize open ai requests
- add questions, answers and reactions (- enable confluence edit or new page recommendation)
- add credibility rating to database 
- trivia question collector 
- consider removing assistants all together



## Setup
Still in forming phase
For now clone the repo
There is one module in each package
Familiarize yourself with the modules
````
git clone https://github.com/MDGrey33/Nur.git
````
Run setup script inside setup package.


## Usage
1. Add openai api key to credentials
2. Add confluence credentials to ./credentials
3. Add project absolute path to ./configuration
4. To listen to slack create slack app and add the credentials in ./credentials
5. Run with python the module main.py clone a space and run the slack bot
8. Go to slack, channel test and ask a question and the bot will reply
