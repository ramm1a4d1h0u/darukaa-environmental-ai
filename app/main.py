from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from app.models import EnvironmentalInput
from app.pipeline import run_environmental_analysis
from app.llm_report import generate_scientific_report
from app.chat import chat_with_environmental_scientist


app = FastAPI(title="Darukaa Earth AI")


# --------------------------------------------------
# CHAT REQUEST MODEL
# --------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse(
        Path(__file__).resolve().parent.parent
        / "static"
        / "index.html"
    )


# --------------------------------------------------
# ENVIRONMENTAL ANALYSIS
# --------------------------------------------------

@app.post("/analyze")
def analyze_environment(data: EnvironmentalInput):

    # -----------------------------------------
    # 1. Run environmental analysis
    # -----------------------------------------

    result = run_environmental_analysis(
        data,
        top_k=5,
        top_n=3
    )

    # -----------------------------------------
    # 2. Generate scientific report using Gemini
    # -----------------------------------------

    report = generate_scientific_report(result)

    # -----------------------------------------
    # 3. Return complete response
    # -----------------------------------------

    return {
        "environmental_context": data.model_dump(),
        "analysis": result,
        "scientific_report": report
    }


# --------------------------------------------------
# CONVERSATIONAL ENVIRONMENTAL SCIENTIST
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    result = chat_with_environmental_scientist(
        session_id=request.session_id,
        message=request.message
    )

    return result