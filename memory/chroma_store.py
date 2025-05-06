import chromadb
from datetime import datetime

class ChromaMemoryStore:
    def __init__(self, collection_name: str = "chat_memory"):
        # ✅ Connect to the running ChromaDB server (must be started with `chroma run`)
        self.client = chromadb.HttpClient(host="localhost", port=8000)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def append_message(self, role: str, content: str):
        timestamp = datetime.utcnow().isoformat()
        self.collection.add(
            documents=[content],
            metadatas=[{"role": role, "timestamp": timestamp}],
            ids=[f"{role}-{timestamp}"]
        )

    def get_messages(self):
        results = self.collection.get(include=["documents", "metadatas"])
        messages = []
        for doc, meta in zip(results["documents"], results["metadatas"]):
            messages.append({
                "role": meta.get("role", "user"),
                "content": doc,
                "timestamp": meta.get("timestamp", "")
            })
        messages.sort(key=lambda m: m["timestamp"])
        return messages

    def clear(self):
        self.collection.delete(where={})  # Delete all stored messages
