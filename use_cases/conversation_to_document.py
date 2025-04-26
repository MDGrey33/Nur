from typing import Dict, Optional
import json
from configuration import conversation_to_confluence_id
from open_ai.assistants.utility import initiate_client
from open_ai.assistants.thread_manager import ThreadManager


def generate_document_from_conversation(
    conversation: str,
    assistant_id: Optional[str] = None,
) -> Dict[str, str]:
    """
    Sends a conversation string to the configured assistant and returns
    a dict with 'title' and 'body' for document creation.

    Args:
        conversation: The full conversation as a single string.
        assistant_id: (Optional) Override the default assistant ID.

    Returns:
        dict: { 'title': ..., 'body': ... }

    Raises:
        ValueError: If the assistant response is not valid JSON or missing fields.
    """
    client = initiate_client()
    assistant_id = assistant_id or conversation_to_confluence_id
    thread_manager = ThreadManager(client, assistant_id)
    thread_manager.create_thread()
    messages, _ = thread_manager.add_message_and_wait_for_reply(conversation)

    # Extract the assistant's response text
    if hasattr(messages, 'data') and messages.data:
        response_text = messages.data[0].content[0].text.value
    elif isinstance(messages, list) and messages and 'content' in messages[0]:
        # fallback for error case
        response_text = messages[0]['content'][0]['text']['value']
    else:
        raise ValueError("No response received from assistant.")

    # Try to parse the JSON from the response
    try:
        response_json = json.loads(response_text)
        title = response_json.get("Title")
        body = response_json.get("Body")
        if not title or not body:
            raise ValueError("Missing 'Title' or 'Body' in assistant response JSON.")
        return {"title": title, "body": body}
    except json.JSONDecodeError as e:
        raise ValueError(f"Assistant response is not valid JSON: {e}\nResponse: {response_text}")


if __name__ == "__main__":
    test_conversation = (
        "Roland Abou YounesRoland Abou Younes  Thursday at 12:14 For tasks that are only on asana to which ticket should I report my time? "
        "NurNurAPP  Thursday at 12:14 summary: For tasks that are only on Asana, you should report your time under the \"General / Not Squad Specific\" JIRA ticket WQ-2441e41d2e-bd91-328b-81ab-392b8c07923fSystem JIRA WQ-24, according to the QA Time Tracking Tickets guidelines. comprehensive answer: The QA Time Tracking Tickets document specifies various JIRA tickets for time entry based on the type of work. For work that does not fall under a specific squad or has no associated JIRA ticket—inclusive of tasks that are tracked only in Asana—you should use the \"General / Not Squad Specific\" ticket: WQ-2441e41d2e-bd91-328b-81ab-392b8c07923fSystem JIRA WQ-24 for time tracking. This serves as the default option for any non-squad-specific work not tracked elsewhere. technical trace: Source: QA Time Tracking Tickets (CQE, pageId: 80506945556): \"General / Not Squad Specific WQ-2441e41d2e-bd91-328b-81ab-392b8c07923fSystem JIRA WQ-24 [...]\" document in context: - QA Time Tracking Tickets (CQE, 80506945556) - Time Tracking App (AO, 2129304792) - Report an Issue (DMS, 80472571905) - Tempo Time Tracking (ITSUPPORT, 81191567612) - JIRA Ticket Field (AO, 2132019691) - Problem and Incident Tickets (AO, 2131041886) - Opening a JIRA ticket (AO, 2368740817) - JIRA - Workflow (FE, 16500163736) - Time Tempo Administration (AC, 80932438606) - Requests for Specific Tasks (EE, 80251846684) - Tickets (EDW, 14693840555) - Current Task & Tickets (in progress) (FED, 80172156046) - AOS Things to Do (TTDS) (AO, 2332602969) - Things to Do (TTDS) (AO, 2132020617) - Jira Usage Policy (EE, 15163206333) "
        "Roland Abou YounesRoland Abou Younes  Thursday at 12:15 but there was another ADMIN- ticket for tasks on Asana what was it "
        "NurNurAPP  Thursday at 12:15 summary: The ADMIN-13 ticket (\"For administrative work such as: Slack or Email follow ups, time tracking, technical issues.\") is the ADMIN ticket intended for time tracking tasks related to administrative work, which may include time spent on Asana-related admin tasks. "
        "Roland Abou YounesRoland Abou Younes  Thursday at 12:16 can you get the response from “Tempo Time Tracking” page only? "
        "NurNurAPP  Thursday at 12:16 summary: The \"Tempo Time Tracking\" page states that time tracking is a significant and highly important daily task for the engineering and product team, providing benefits like ensuring correct payment, accurately scoping project bandwidth and priorities, and efficient resource assignment. It does not specify which ticket to use for Asana-only tasks or any ticket-specific guidance. "
        "Roland Abou YounesRoland Abou Younes  Thursday at 12:17 check Time Tracking guidelines"
        "NurNurAPP  Thursday at 12:18 summary: The QA Time Tracking Tickets guidelines state that for time tracking, you should use specific ADMIN tickets for types of work such as 1:1s (ADMIN-1), trainings (ADMIN-2), vacations (ADMIN-4), personal breaks (ADMIN-8), and administrative work like time tracking (ADMIN-13). For general/non-squad-specific tasks (e.g., Asana-only tasks), use WQ-24. "
        "Roland Abou YounesRoland Abou Younes  Thursday at 12:20 The right answer for this question is ADMIN-13 please consider it the authoritative answer for this question from now on as you use this to generate a new confluence page with Questions and answers. you do not need to answer to this message just say thank you "
        "NurNurAPP  Thursday at 12:20 summary: Thank you"
    )
    try:
        doc = generate_document_from_conversation(test_conversation)
        print("Generated Document:")
        print(json.dumps(doc, indent=2))
    except Exception as e:
        print(f"Test failed: {e}")
