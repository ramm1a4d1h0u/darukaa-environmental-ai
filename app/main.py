from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
import threading

from app.chat import chat_with_environmental_scientist


app = FastAPI(
    title="Darukaa Earth AI Environmental Scientist"
)


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


@app.get("/")
def home():
    return FileResponse(
        STATIC_DIR / "index.html"
    )


@app.post("/chat")
def chat(request: dict):

    session_id = request.get(
        "session_id",
        "default"
    )

    message = request.get(
        "message",
        ""
    )

    return chat_with_environmental_scientist(
        session_id,
        message
    )


def initialize_rag():

    try:

        from app.rag import collection, build_knowledge_base

        count = collection.count()

        if count == 0:

            print(
                "Knowledge base is empty. "
                "Building knowledge base..."
            )

            build_knowledge_base()

        else:

            print(
                f"Knowledge base already contains "
                f"{count} documents."
            )

    except Exception as e:

        print(
            f"RAG initialization failed: {e}"
        )


@app.on_event("startup")
def startup_event():

    thread = threading.Thread(
        target=initialize_rag,
        daemon=True
    )

    thread.start()