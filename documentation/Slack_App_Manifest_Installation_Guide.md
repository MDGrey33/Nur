# Slack App Manifest Installation Guide

This guide will walk you through the process of obtaining a Slack app manifest file from a local directory and installing it in your own Slack workspace. The manifest file contains all the necessary configurations for a Slack app, allowing you to replicate an app setup easily.

## Prerequisites

Before you begin, ensure you have the following:
- A Slack account with permissions to create apps in your workspace.
- The Slack app manifest file, typically named `manifest.yml`, located in your local `./documentation/slack/` directory.
- Access to the Slack API website.

## Step 1: Obtain the Manifest File

Locate the `manifest.yml` file in your local directory structure. The file path should be `./documentation/slack/manifest.yml`. 

If you're using a terminal or command line interface, you can navigate to the directory containing the manifest file using:

```bash
cd path/to/slack
```

Ensure the `manifest.yml` file exists by listing the contents of the directory:

```bash
ls
```

## Step 2: Access Slack API Dashboard

1. Open your web browser and navigate to the [Slack API website](https://api.slack.com/apps).
2. Log in with your Slack credentials if prompted.

## Step 3: Create a New Slack App

1. Click on **Create New App**.
2. Choose the **From an app manifest** option.
3. Select the Slack workspace where you want to install the app.

## Step 4: Upload Your Manifest File

1. When prompted to choose how to configure your app, select **YAML**.
2. Copy the contents of your `manifest.yml` file. This can be done by opening the file in a text editor, selecting all content (`Ctrl+A` or `Cmd+A`), and copying it (`Ctrl+C` or `Cmd+C`).
3. Paste the copied contents into the text area provided on the Slack API website.
4. Click the **Next** button to proceed.

## Step 5: Review Your App Configuration

1. Slack will parse the manifest file and display a summary of your app's configuration. Review this information to ensure it matches your expectations.
2. If everything looks correct, click **Create**.

## Step 6: Install Your App

After creating your app, you'll be directed to the app's Basic Information page. From here:

1. Navigate to the **Install App** section in the sidebar.
2. Click on **Install App to Workspace**.
3. Follow the prompts to authorize the app in your workspace.

## Conclusion

Your Slack app, as defined in the `manifest.yml` file, is now installed in your workspace. You can now navigate to your Slack workspace to interact with your app or continue to configure and customize it through the Slack API dashboard.

For further customization or troubleshooting, refer to the [official Slack API documentation](https://api.slack.com/docs).