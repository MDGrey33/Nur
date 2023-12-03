# Nur
The self actualizing documentation framework that heals its knowledge gaps as naturally as a ray of light
[Custom GPT to discuss the code base](https://chat.openai.com/g/g-zKBLXtfrD-shams-nur)
## Feature list
### Done:
- add a confluence space (url credentials and update interval) 
- Pulls the confluence space and stores it in a sqlite database
- Vectorizes the confluence space pages and stores the embeds in a chroma db collection
- Uses the vectorized embeds to find the most similar pages to a question
### Todo:
- Creates an assistant with the relevant pages and allows it to engage to provide the answer if confident enough
- Listens on specific slack channels for questions relevant to its domain
- Gets user feedback to either increase confidence or decrease confidence
- If confidence is below a certain threashold the assistant will add the question to a trivia quizz and runs it with the specialist team and recommends the update in a confluence comment


## Setup
Still n forming phase
For now clone the repo
There is one module in each package
Familiarize yourself with the modules
````
git clone https://github.com/MDGrey33/Nur.git
````
Setup script not functional at this point.
