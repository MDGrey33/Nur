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
- Move slack processed ids to sqlite database
- move away from persist queue due to lack of support in python 3.11
- Address the multiple processors issue in persist queue that causes a pickle
- Address idempotency in sync-up QnA to confluence
- setup last update date and schedule to update confluence space with log in db
- store embeds in database
- create new vector database nightly and on trigger from sql database
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
3. Add project absolute path to ./confiduration
4. To listen to slack create slack app and add bot_user_id to ./configuration
5. Run with python the module ./confluence_integration/retrieve_confluence_space.py
6. Run with python the module ./vector/chrome
7. Run with pythin the modul ./slack/channel_reaction.py
8. Go to slack, channel test and ask a question and the bot will reply
