
## Setup the project

Clone branch nur\modular to folder Nur
```warp-runnable-command
git clone -b modular https://github.com/mdgrey33/nur.git Nur
```
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
# Setup a dummy account in confluence and use it's details here
CONFLUENCE_TEST_URL=https://abouyounes.atlassian.net/
CONFLUENCE_TEST_USERNAME=roland@abouyounes.com
CONFLUENCE_TEST_API_TOKEN=key

# OpenAI Key
# Setup an account in openai and use it's key here
OPEN_AI_KEY=key
```
Bring the docker machines up
```warp-runnable-command
docker-compose up -d
```

Run the project

```warp-runnable-command
poetry run uvicorn nurai.main:app --reload
```
To make pycharm work for you\, open a new project in pycharm and point it to  Nur\/nurai
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

## Access the mysql database

```warp-runnable-command
mysql -h127.0.0.1 -P3306 -uuser -ppassword
```

## Run the project

Go to the folder you cloned Nur to and thne to the folder nurai where we have the poetry package
```warp-runnable-command
cd code/Nur
```
Get latest updates from git
```warp-runnable-command
git pull origin modular
```
Move to the poetry package
```warp-runnable-command
cd nurai
```
Install poetry
```warp-runnable-command
poetry install
```
Run the project
```warp-runnable-command
poetry run gunicorn -k uvicorn.workers.UvicornWorker -w 4 nurai.main:app
```
To access the database
```warp-runnable-command
mysql -h127.0.0.1 -P3306 -uuser -ppassword
```

## Add a new data model using Alembic


```warp-runnable-command
# Move to the poetry package
cd code/nur/nurai
# Import the model in /nurai/migrations/env.py
# Create a new migration
poetry run alembic revision --autogenerate -m "Initialize the db"
# Apply the migration
poetry run alembic upgrade head
```

## Instructions for using Cursor

# Always prefix your #i instructions with 

```
Knowing the project is in migration, we need to move fromt he old functionality under Nur to the new functionality under Nur/nurai where we are using the factory pattern
```
