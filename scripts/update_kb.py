import chromadb
import sys

# Add the project root to the Python path to allow importing from 'data'
sys.path.append(".")
from data.new_market_data_source import fetch_new_trends


def main():
    print("Connecting to persistent Knowledge Base...")
    # IMPORTANT: Connect to the same persistent client as the main app
    client = chromadb.PersistentClient(path="./db")
    collection = client.get_or_create_collection("resume_insights_knowledge_base")

    # Fetch new data
    new_trends = fetch_new_trends()

    if not new_trends:
        print("No new trends to add.")
        return

    print(f"Found {len(new_trends)} new trends to add to the knowledge base.")

    # Prepare data for upserting
    documents = [item["content"] for item in new_trends]
    metadata = [item["metadata"] for item in new_trends]
    ids = [item["id"] for item in new_trends]

    # Use 'upsert' to add new documents or update existing ones if IDs match.
    # This prevents adding duplicate data if the script is run multiple times.
    collection.upsert(ids=ids, metadatas=metadata, documents=documents)

    print("Knowledge Base successfully updated.")
    print(f"Total documents in collection: {collection.count()}")


if __name__ == "__main__":
    main()
