## all messages seem to be received 4 times

### This is a simple message on a channel

```
[32m2024-04-07 01:36:58 - handle - INFO - Received payload: {
    "token": "Uohe5GDtysBv71UhkyB5G8bN",
    "team_id": "T02493EGZ4N",
    "context_team_id": "T02493EGZ4N",
    "context_enterprise_id": null,
    "api_app_id": "A068JQEJ4BZ",
    "event": {
        "user": "U024UF2F68H",
        "type": "message",
        "ts": "1712443018.659929",
        "client_msg_id": "f9b78c94-0f24-4bbc-a204-403f13511c26",
        "text": "This is a simple message on a channel",
        "team": "T02493EGZ4N",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "jdzU7",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "This is a simple message on a channel"
                            }
                        ]
                    }
                ]
            }
        ],
        "channel": "C06EGCDNA4A",
        "event_ts": "1712443018.659929",
        "channel_type": "group"
    },
    "type": "event_callback",
    "event_id": "Ev06SQ9VPA95",
    "event_time": 1712443018,
    "authorizations": [
        {
            "enterprise_id": null,
            "team_id": "T02493EGZ4N",
            "user_id": "U069C17DCE5",
            "is_bot": true,
            "is_enterprise_install": false
        }
    ],
    "is_ext_shared_channel": false,
    "event_context": "4-eyJldCI6Im1lc3NhZ2UiLCJ0aWQiOiJUMDI0OTNFR1o0TiIsImFpZCI6IkEwNjhKUUVKNEJaIiwiY2lkIjoiQzA2RUdDRE5BNEEifQ"
}[0m
```

### this is a reply to the message in thread
```
[32m2024-04-07 01:38:44 - handle - INFO - Received payload: {
    "token": "Uohe5GDtysBv71UhkyB5G8bN",
    "team_id": "T02493EGZ4N",
    "context_team_id": "T02493EGZ4N",
    "context_enterprise_id": null,
    "api_app_id": "A068JQEJ4BZ",
    "event": {
        "user": "U024UF2F68H",
        "type": "message",
        "ts": "1712443121.047909",
        "client_msg_id": "e838ac8f-a26a-429a-970d-5af7dd4a0abb",
        "text": "this is a reply to the message in thread",
        "team": "T02493EGZ4N",
        "thread_ts": "1712443018.659929",
        "parent_user_id": "U024UF2F68H",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "saga/",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "this is a reply to the message in thread"
                            }
                        ]
                    }
                ]
            }
        ],
        "channel": "C06EGCDNA4A",
        "event_ts": "1712443121.047909",
        "channel_type": "group"
    },
    "type": "event_callback",
    "event_id": "Ev06T1UTN5BP",
    "event_time": 1712443121,
    "authorizations": [
        {
            "enterprise_id": null,
            "team_id": "T02493EGZ4N",
            "user_id": "U069C17DCE5",
            "is_bot": true,
            "is_enterprise_install": false
        }
    ],
    "is_ext_shared_channel": false,
    "event_context": "4-eyJldCI6Im1lc3NhZ2UiLCJ0aWQiOiJUMDI0OTNFR1o0TiIsImFpZCI6IkEwNjhKUUVKNEJaIiwiY2lkIjoiQzA2RUdDRE5BNEEifQ"
}[0m
```
### Bookmark reaction on a channel
```
[32m2024-04-07 01:42:54 - handle - INFO - Received payload: {
    "token": "Uohe5GDtysBv71UhkyB5G8bN",
    "team_id": "T02493EGZ4N",
    "context_team_id": "T02493EGZ4N",
    "context_enterprise_id": null,
    "api_app_id": "A068JQEJ4BZ",
    "event": {
        "type": "reaction_added",
        "user": "U024UF2F68H",
        "reaction": "bookmark",
        "item": {
            "type": "message",
            "channel": "C06EGCDNA4A",
            "ts": "1712443018.659929"
        },
        "item_user": "U024UF2F68H",
        "event_ts": "1712443373.000200"
    },
    "type": "event_callback",
    "event_id": "Ev06SQA1PQBH",
    "event_time": 1712443373,
    "authorizations": [
        {
            "enterprise_id": null,
            "team_id": "T02493EGZ4N",
            "user_id": "U069C17DCE5",
            "is_bot": true,
            "is_enterprise_install": false
        }
    ],
    "is_ext_shared_channel": false,
    "event_context": "4-eyJldCI6InJlYWN0aW9uX2FkZGVkIiwidGlkIjoiVDAyNDkzRUdaNE4iLCJhaWQiOiJBMDY4SlFFSjRCWiIsImNpZCI6IkMwNkVHQ0ROQTRBIn0"
}[0m
```
### Bookmark reaction on a reply
```
[32m2024-04-07 01:44:13 - handle - INFO - Received payload: {
    "token": "Uohe5GDtysBv71UhkyB5G8bN",
    "team_id": "T02493EGZ4N",
    "context_team_id": "T02493EGZ4N",
    "context_enterprise_id": null,
    "api_app_id": "A068JQEJ4BZ",
    "event": {
        "type": "reaction_added",
        "user": "U024UF2F68H",
        "reaction": "bookmark",
        "item": {
            "type": "message",
            "channel": "C06EGCDNA4A",
            "ts": "1712443121.047909"
        },
        "item_user": "U024UF2F68H",
        "event_ts": "1712443449.000300"
    },
    "type": "event_callback",
    "event_id": "Ev06T4SL2G4A",
    "event_time": 1712443449,
    "authorizations": [
        {
            "enterprise_id": null,
            "team_id": "T02493EGZ4N",
            "user_id": "U069C17DCE5",
            "is_bot": true,
            "is_enterprise_install": false
        }
    ],
    "is_ext_shared_channel": false,
    "event_context": "4-eyJldCI6InJlYWN0aW9uX2FkZGVkIiwidGlkIjoiVDAyNDkzRUdaNE4iLCJhaWQiOiJBMDY4SlFFSjRCWiIsImNpZCI6IkMwNkVHQ0ROQTRBIn0"
}[0m
```


### Bot mention in the channel
```
[32m2024-04-07 01:46:11 - handle - INFO - Received payload: {
    "token": "Uohe5GDtysBv71UhkyB5G8bN",
    "team_id": "T02493EGZ4N",
    "context_team_id": "T02493EGZ4N",
    "context_enterprise_id": null,
    "api_app_id": "A068JQEJ4BZ",
    "event": {
        "user": "U024UF2F68H",
        "type": "message",
        "ts": "1712443567.176719",
        "client_msg_id": "dbac0ecb-3a6d-4371-8589-efecfce0246c",
        "text": "<@U069C17DCE5> This is a mention of the bot in the channel",
        "team": "T02493EGZ4N",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "qgrlU",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "user",
                                "user_id": "U069C17DCE5"
                            },
                            {
                                "type": "text",
                                "text": " This is a mention of the bot in the channel"
                            }
                        ]
                    }
                ]
            }
        ],
        "channel": "C06EGCDNA4A",
        "event_ts": "1712443567.176719",
        "channel_type": "group"
    },
    "type": "event_callback",
    "event_id": "Ev06SQA5793R",
    "event_time": 1712443567,
    "authorizations": [
        {
            "enterprise_id": null,
            "team_id": "T02493EGZ4N",
            "user_id": "U069C17DCE5",
            "is_bot": true,
            "is_enterprise_install": false
        }
    ],
    "is_ext_shared_channel": false,
    "event_context": "4-eyJldCI6Im1lc3NhZ2UiLCJ0aWQiOiJUMDI0OTNFR1o0TiIsImFpZCI6IkEwNjhKUUVKNEJaIiwiY2lkIjoiQzA2RUdDRE5BNEEifQ"
}[0m
```
### Bot mention in a thread
```
[32m2024-04-07 01:47:47 - handle - INFO - Received payload: {
    "token": "Uohe5GDtysBv71UhkyB5G8bN",
    "team_id": "T02493EGZ4N",
    "api_app_id": "A068JQEJ4BZ",
    "event": {
        "user": "U024UF2F68H",
        "type": "app_mention",
        "ts": "1712443664.016049",
        "client_msg_id": "eff74227-7296-4a35-aef5-6e613b954ece",
        "text": "<@U069C17DCE5> Mention of the bot in a reply in thread",
        "team": "T02493EGZ4N",
        "thread_ts": "1712443567.176719",
        "parent_user_id": "U024UF2F68H",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "uR81D",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "user",
                                "user_id": "U069C17DCE5"
                            },
                            {
                                "type": "text",
                                "text": " Mention of the bot in a reply in thread"
                            }
                        ]
                    }
                ]
            }
        ],
        "channel": "C06EGCDNA4A",
        "event_ts": "1712443664.016049"
    },
    "type": "event_callback",
    "event_id": "Ev06T1V35HCM",
    "event_time": 1712443664,
    "authorizations": [
        {
            "enterprise_id": null,
            "team_id": "T02493EGZ4N",
            "user_id": "U069C17DCE5",
            "is_bot": true,
            "is_enterprise_install": false
        }
    ],
    "is_ext_shared_channel": false,
    "event_context": "4-eyJldCI6ImFwcF9tZW50aW9uIiwidGlkIjoiVDAyNDkzRUdaNE4iLCJhaWQiOiJBMDY4SlFFSjRCWiIsImNpZCI6IkMwNkVHQ0ROQTRBIn0"
}[0m
```

### Bot direct message
```
[32m2024-04-07 01:50:22 - handle - INFO - Received payload: {
    "token": "Uohe5GDtysBv71UhkyB5G8bN",
    "team_id": "T02493EGZ4N",
    "context_team_id": "T02493EGZ4N",
    "context_enterprise_id": null,
    "api_app_id": "A068JQEJ4BZ",
    "event": {
        "user": "U024UF2F68H",
        "type": "message",
        "ts": "1712443819.359919",
        "client_msg_id": "9110765a-a53a-400b-9edc-a3961044aa68",
        "text": "This is a direct message to the bot in private",
        "team": "T02493EGZ4N",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "yT/Oy",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "This is a direct message to the bot in private"
                            }
                        ]
                    }
                ]
            }
        ],
        "channel": "D069N5MSX4Y",
        "event_ts": "1712443819.359919",
        "channel_type": "im"
    },
    "type": "event_callback",
    "event_id": "Ev06T4SSK2BU",
    "event_time": 1712443819,
    "authorizations": [
        {
            "enterprise_id": null,
            "team_id": "T02493EGZ4N",
            "user_id": "U069C17DCE5",
            "is_bot": true,
            "is_enterprise_install": false
        }
    ],
    "is_ext_shared_channel": false,
    "event_context": "4-eyJldCI6Im1lc3NhZ2UiLCJ0aWQiOiJUMDI0OTNFR1o0TiIsImFpZCI6IkEwNjhKUUVKNEJaIiwiY2lkIjoiRDA2OU41TVNYNFkifQ"
}[0m
```
