import chromadb
from chromadb import Settings


def get_chroma():
    return chromadb.HttpClient(
        host="127.0.0.1",
        port=8001,
        settings=Settings(allow_reset=True, anonymized_telemetry=False),
    )
