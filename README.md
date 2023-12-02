# Nur
The self actualizing documentation framework that heals its knowledge gaps as naturally as a ray of light

## Feature list
### Done:
- add a confluence space (url credentials and update interval) 
- Pulls the confluence space and stores it in an sqlite database
- Vectorizes the confluence space pages and stores the embeds in a chroma db collection
- Uses the vectorized embeds to find the most similar pages to a question
### Todo:
- Creates an assistant with the relevant pages and allows it to engage to provide the answer if confident enough
- Listens on specific slack channels for questions relevant to its domain
- Gets user feedback to either increase confidence or decrease confidence
- If confidence is below a certain threashold the assistant will add the question to a trivia quizz and runs it with the specialist team and recommends the update in a confluence comment


## Setup


````
git clone https://github.com/MDGrey33/Nur.git
````
Download setup_and_run.sh from the repo and make it executable and execute it

````
cd Nur
chmod +x ./setup/setup_and_run.sh
./setup/setup_and_run.sh
````

The script will load 3 docker images for you 1 of which is the python environment and 2 are Kafka and Kafka Zookeeper 

or follow the steps in the script manually.

Ref: 
API documentation: https://atlassian-python-api.readthedocs.io/confluence.html
