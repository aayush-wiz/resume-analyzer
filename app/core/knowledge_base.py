import chromadb

client = chromadb.PersistentClient(path="./db")

collection = client.get_or_create_collection("resume_insights_knowledge_base")

def initialize_knowledge_base():
    """Loads the INITIAL data into the ChromaDB collection if it's empty."""
    from data.market_trends import knowledge_base_data  # Import it locally

    if collection.count() == 0:
        print("Initializing Knowledge Base for the first time...")
        documents = [item["content"] for item in knowledge_base_data]
        metadata = [item["metadata"] for item in knowledge_base_data]
        ids = [item["id"] for item in knowledge_base_data]
        collection.add(documents=documents, metadatas=metadata, ids=ids)
        print("Knowledge Base Initialized.")
    else:
        print("Knowledge Base already contains data. Skipping initialization.")


def query_knowledge_base(query_text: str, n_results: int = 5) -> list[str]:
    """Queries the knowledge base to find relevant context."""
    try:
        results = collection.query(query_texts=[query_text], n_results=n_results)
        if not results["documents"]:
            return []
        return results["documents"][0]
    except Exception as e:
        print(f"Error querying knowledge base: {e}")
        # Return empty list as fallback
        return []
