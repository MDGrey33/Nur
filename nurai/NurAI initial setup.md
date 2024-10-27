Clone the Repo modular branch
Go to the folder you cloned Nur to and thne to the folder nurai where we have the poetry package
```warp-runnable-command
cd Nur/nurai
```
Install poetry
```warp-runnable-command
poetry install
```
Add the \.env file as follows
```text
PYTHONPATH="/Users/roland/code/Nur:$PYTHONPATH"
NUR_API_HOST="localhost"
NUR_API_PORT=8001

#app .env

# Confluence Test Credentials
CONFLUENCE_TEST_URL=https://abouyounes.atlassian.net/
CONFLUENCE_TEST_USERNAME=roland@abouyounes.com
CONFLUENCE_TEST_API_TOKEN=yourconfluencetoken

# OpenAI Key
OPEN_AI_KEY=youropenaitoken
```
Run the project 

```warp-runnable-command
poetry run uvicorn nurai.main:app --reload
```
To make pycharm work for you\, open a new project in pycharm and point it to  nur\/nurai
When it says creating virtual environment click cancle
then go to interpreter settings 
click the dropdown
show all
\+
click poetry environment then select existing
get your poetry interpreter

```warp-runnable-command
poetry env info
```
copy virtual env executable and past it in pycharm
click ok and you hsould be ready to go\, now your ide will identify missing packages and all