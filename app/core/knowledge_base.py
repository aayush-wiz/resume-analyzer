import chromadb
import google.generativeai as genai
from data.market_trends import knowledge_base_data

# Use an in-memory client for simplicity
client = chromadb.Client()

# Create a collection to store our knowledge base
# The embedding_function is automatically handled by ChromaDB if not specified,
# but for production, explicit model selection is better.
collection = client.get_or_create_collection("resume_insights_knowledge_base")


def initialize_knowledge_base():
    """Loads data into the ChromaDB collection."""
    if collection.count() == 0:
        print("Initializing Knowledge Base...")
        documents = [item["content"] for item in knowledge_base_data]
        metadata = [item["metadata"] for item in knowledge_base_data]
        ids = [item["id"] for item in knowledge_base_data]

        collection.add(documents=documents, metadatas=metadata, ids=ids)
        print("Knowledge Base Initialized.")
    else:
        print("Knowledge Base already initialized.")


def query_knowledge_base(query_text: str, n_results: int = 3) -> list[str]:
    """Queries the knowledge base to find relevant context."""
    results = collection.query(query_texts=[query_text], n_results=n_results)
    return results["documents"][0]
