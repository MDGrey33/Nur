---
title: Developer Commands for Nur Project
---
## Setting Up Your Development Environment

First, navigate to your project's root directory. Update the path in the command below to match your project folder path.

```bash
cd /path/to/your/Nur/project
```

**Note:** Replace `/path/to/your/Nur/project` with the absolute path to your Nur project folder.

Set the environment variables required for the project to run. Ensure to update the path to the `Nur` project folder to match your specific setup.

```bash
export PYTHONPATH="/absolute/path/to/your/Nur/:$PYTHONPATH" && export NUR_API_PORT=8001 && export NUR_API_HOST="localhost" && echo "Environment variables set."
```

**Important:** Change `/absolute/path/to/your/Nur/` to the absolute path of your project directory. This is crucial for the project to access its packages and modules correctly.

## Starting the Services

### Start the API Server

```bash
poetry run python ./api/endpoint.py
```

### Start the Slack Bot

```bash
poetry run python ./slack/bot.py
```

### Start the Management Console

This console links to all the functionality provided by the Nur project.

```bash
poetry run python ./main.py
```

## Clearing the Content Folder

To start from scratch, you might want to clear the content folder. Here are the commands to do so safely:

```bash
echo "Deleting the contents of the directory: "
rm -rf ~/absolute/path/to/Nur/content/* 2> /dev/null || true

echo "Creating directories: database, file_system, transactional"
mkdir -p ~/absolute/path/to/Nur/content/database ~/absolute/path/to/Nur/content/file_system ~/absolute/path/to/Nur/content/transactional

echo "Creating .include files in each directory"
touch ~/absolute/path/to/Nur/content/database/.include ~/absolute/path/to/Nur/content/file_system/.include ~/absolute/path/to/Nur/content/transactional/.include

echo "Cleanup completed successfully."
```

**Note:** Make sure to replace `~/absolute/path/to/Nur/` with the absolute path to your project's `content` directory to ensure the commands execute correctly.