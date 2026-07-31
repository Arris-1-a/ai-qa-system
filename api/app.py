"""RESTful API for the AI Question Answering System."""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import asyncio
import time

from main import QASystem, AnswerResult

app = FastAPI(
    title="AI Q&A System API",
    description="Intelligent question answering with vector search and LLM generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

qa_system = QASystem()


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="User's question")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of source documents to retrieve")


class AskResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Dict]
    query_time_ms: int
    conversation_id: str
    timestamp: str


class StatsResponse(BaseModel):
    status: str
    document_count: int
    conversation_count: int
    initialized: bool


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    global qa_system
    if request.top_k != 5:
        qa_system.config['search']['top_k'] = request.top_k

    if not qa_system.is_initialized:
        await qa_system.initialize()

    try:
        result = await qa_system.ask(request.question, request.conversation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return AskResponse(
        answer=result.answer,
        confidence=result.confidence,
        sources=[
            {"id": s["id"], "content": s["content"][:300] + ("..." if len(s["content"]) > 300 else ""),
             "score": s.get("score", 0)}
            for s in result.source_documents
        ],
        query_time_ms=result.query_time_ms,
        conversation_id=result.conversation_id,
        timestamp=result.timestamp
    )


@app.post("/documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    contents = []
    for f in files:
        content = await f.read()
        text = content.decode('utf-8').strip()
        if text:
            contents.append(text)
    if contents:
        qa_system.add_documents(contents)
    return {"added": len(contents), "status": "ok"}


@app.get("/status", response_model=StatsResponse)
async def get_status():
    stats = qa_system.get_stats()
    return StatsResponse(
        status="running" if qa_system.is_initialized else "initializing",
        document_count=stats['document_count'],
        conversation_count=stats['active_conversations'],
        initialized=stats['initialized']
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}


@app.on_event("startup")
async def startup():
    await qa_system.initialize()
