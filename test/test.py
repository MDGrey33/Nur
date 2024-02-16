'''
import chromadb
from chromadb.config import Settings

# Initialize the Chroma client
client = chromadb.Client(Settings())

# Create a new collection with a specified name
collection_name = "test_collection"
collection = client.create_collection(collection_name)

# Define embeddings and their IDs
embeddings = [
    [0.1, 0.2, 0.3, 0.4],
    [0.5, 0.6, 0.7, 0.8]
]
ids = ["item1", "item2"]

# Add embeddings to the collection
collection.add(embeddings=embeddings, ids=ids)

# Retrieve embeddings by IDs
retrieved_embeddings = collection.get(ids=ids, include=["metadatas", "documents", "embeddings"])

print(f"Retrieved embeddings: {retrieved_embeddings}")

# Perform a similarity search
query_embedding = [0.15, 0.25, 0.35, 0.45]
similar_items = collection.query(query_embeddings=[query_embedding],
                                 n_results=2)
print(f"Similar items: {similar_items}")


from main import ask_question
from vector.chroma_threads import retrieve_relevant_documents_chroma as retrieve_relevant_documents
from oai_assistants.query_assistant_from_documents import query_assistant_with_context


def answer_question_with_assistant(question):
    relevant_document_ids = retrieve_relevant_documents(question)
    response, thread_id = query_assistant_with_context(question, relevant_document_ids)
    return response, thread_id

question = ask_question()
if question:
    answer, thread_id = answer_question_with_assistant(question)
    print(f"\nThread ID: {thread_id}\nAnswer: {answer}")


from slack.event_consumer import EventConsumer
from slack.event_consumer import QuestionEvent
question_event = QuestionEvent(text="What are the positions for engineers in the billing team?",
                               ts="1234567890",
                               thread_ts="1234567890",
                               channel="C123456",
                               user="U123456")

# create an instance of the event consumer
ec = EventConsumer()
# ask question using process question
ec.process_question(question_event)
'''



