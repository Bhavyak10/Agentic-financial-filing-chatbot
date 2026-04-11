from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.agent.graph import build_graph

app = FastAPI(title="Financial Filing Chatbot")

graph_app = build_graph()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[str] = []


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = graph_app.invoke({
        "question": req.message,
        "task_type": None,
        "company": None,
        "companies": [],
        "year": None,
        "target_section": None,
        "retrieved_chunks": [],
        "final_answer": None,
    })

    citations = [
        chunk.get("chunk_id")
        for chunk in result.get("retrieved_chunks", [])
        if chunk.get("chunk_id")
    ]

    return {
        "answer": result.get("final_answer", ""),
        "citations": citations,
    }