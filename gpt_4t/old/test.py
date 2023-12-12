import os
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import LLM

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# Function to load and split a text file into chunks
def load_and_split_documents(file_paths):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            text = file.read()
            chunks = splitter.split_text(text)
            documents.extend(chunks)
    return documents

# Set up OpenAI and LangChain
embedding = OpenAIEmbeddings()
vectordb = Chroma("your_vector_store_name", embedding)

# Load and process your documents
file_paths = ["path/to/your/textfile1.txt", "path/to/your/textfile2.txt"]
all_documents = load_and_split_documents(file_paths)

# Index documents in the vector store
for doc in all_documents:
    vectordb.add(doc)

# Test function
def test_query(query):
    similar_docs = vectordb.similarity_search(query)
    context = "\n".join(similar_docs)
    response = openai.Completion.create(prompt=context + query, engine="davinci", max_tokens=150)
    return response.choices[0].text

# Running tests
test_queries = [
    "What is the main theme of the first document?",
    "Explain the process described in the second document."
]

for query in test_queries:
    print(f"Query: {query}")
    print("Response:", test_query(query))
    print("-------------")
