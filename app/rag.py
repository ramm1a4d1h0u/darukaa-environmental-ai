import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# -----------------------------
# Paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_FILE = BASE_DIR / "data" / "knowledge_base.json"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"


# -----------------------------
# Embedding model
# -----------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")


# -----------------------------
# ChromaDB
# -----------------------------

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_or_create_collection(
    name="environmental_knowledge"
)


# -----------------------------
# Load knowledge
# -----------------------------

def load_knowledge():
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# -----------------------------
# Index knowledge
# -----------------------------

def build_knowledge_base():
    knowledge = load_knowledge()

    documents = []
    metadatas = []
    ids = []

    for item in knowledge:

        document = (
            f"Topic: {item['topic']}\n"
            f"Title: {item['title']}\n"
            f"Content: {item['content']}\n"
            f"Environmental metrics: {', '.join(item['metrics'])}\n"
            f"Interventions: {', '.join(item['interventions'])}"
        )

        documents.append(document)

        metadatas.append({
            "topic": item["topic"],
            "title": item["title"],
            "source": item["source"],
            "source_url": item["source_url"]
        })

        ids.append(item["id"])

    embeddings = embedding_model.encode(
        documents,
        normalize_embeddings=True
    ).tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"Indexed {len(documents)} knowledge documents.")


# -----------------------------
# Search knowledge
# -----------------------------

def search_knowledge(query: str, top_k: int = 3):

    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results

def rebuild_knowledge_base():
    global collection

    # Delete the existing collection
    try:
        client.delete_collection("environmental_knowledge")
    except Exception:
        pass

    # Create a fresh collection
    collection = client.create_collection(
        name="environmental_knowledge"
    )

    # Index the new knowledge
    build_knowledge_base()

    print("Knowledge base rebuilt successfully.")

def search_intervention_evidence(
    intervention: str,
    top_k: int = 3
):
    """
    Retrieve scientific evidence specifically related
    to a recommended intervention.
    """

    query = (
        f"Scientific evidence about {intervention} "
        f"and its effects on soil health, biodiversity, "
        f"water management and ecosystem functions."
    )

    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results