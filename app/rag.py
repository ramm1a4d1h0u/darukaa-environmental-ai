import json
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_FILE = BASE_DIR / "data" / "knowledge_base.json"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"


print("Loading Chroma embedding function...")

embedding_function = DefaultEmbeddingFunction()

print("Embedding function loaded.")


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


def load_knowledge():
    with open(
        KNOWLEDGE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def create_collection():
    return client.get_or_create_collection(
        name="environmental_knowledge",
        embedding_function=embedding_function
    )


collection = create_collection()


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
            f"Environmental metrics: "
            f"{', '.join(item['metrics'])}\n"
            f"Interventions: "
            f"{', '.join(item['interventions'])}"
        )

        documents.append(document)

        metadatas.append({
            "topic": item["topic"],
            "title": item["title"],
            "source": item["source"],
            "source_url": item["source_url"]
        })

        ids.append(item["id"])

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(
        f"Indexed {len(documents)} knowledge documents."
    )


# Make sure the knowledge base exists.
# if collection.count() == 0:
#     print("Knowledge base is empty. Building knowledge base...")
#     build_knowledge_base()
# else:
#     print(
#         f"Knowledge base already contains "
#         f"{collection.count()} documents."
#     )


def search_knowledge(
    query: str,
    top_k: int = 3
):

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    return results


def rebuild_knowledge_base():

    global collection

    try:
        client.delete_collection(
            "environmental_knowledge"
        )
    except Exception:
        pass

    collection = client.create_collection(
        name="environmental_knowledge",
        embedding_function=embedding_function
    )

    build_knowledge_base()

    print(
        "Knowledge base rebuilt successfully."
    )


def search_intervention_evidence(
    intervention: str,
    top_k: int = 3
):

    query = (
        f"Scientific evidence about {intervention} "
        f"and its effects on soil health, biodiversity, "
        f"water management and ecosystem functions."
    )

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    return results