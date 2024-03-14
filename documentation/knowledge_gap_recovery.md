---
title: Developer Notes for Knowledge Gap Identification and Documentation Augmentation
---
## Introduction

This document outlines the process and configurations required to identify knowledge gaps in our system documentation through Slack interactions and subsequently augment the Confluence documentation with the new insights gathered.

## Feature Overview

The system is designed to enhance our Confluence documentation by identifying knowledge gaps in specific domains (e.g., billing or infrastructure) using Slack interactions. The process involves:

1.  Retrieving interactions related to the specified domain that indicate a lack of information or unanswered questions.
2.  Reviewing these interactions to compile a list of questions that need answers.
3.  Posting these questions to a predefined Slack channel.
4.  Monitoring the channel for responses until a :white\_check\_mark: reaction is detected on the original question.
5.  Collecting the full conversation and summarizing the outcome.
6.  Creating a new Confluence page with the summary and adding it to a specified space in our Confluence documentation.

This approach allows for the dynamic augmentation of our documentation, ensuring it remains relevant and comprehensive.

## Slack Configuration

- You can retrieve the channel id from the database if the channel you are after has been used for user questions:  
    I included the below in config to stor multiple channel ids
    - `slack_channel_tt_ta_debug` = "C06EA5WFGUF"
    - `slack_channel_tt_ta` = "C052GJ7GLVC"
    - `channel_id` = `slack_channel_priv_tt_ta`

## Confluence Configuration

To set up the Confluence documentation space, use the following configuration:

```python
# System Knowledge space name on Confluence
system_knowledge_space_private = "Nur Documentation"
system_confluence_knowledge_space = system_knowledge_space_private
```

If the specified space exists and the system has access to it, it will utilize the existing space for documentation augmentation.

## Contributing to Information Gathering

The system is being enhanced to automatically include individuals who asked the initial questions in the information gathering effort, as well as the authors of the most relevant topics on Slack. This aims to create a collaborative environment for continuously improving our documentation.

---

For further details or updates, please refer to the system documentation or contact the development team.