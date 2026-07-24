import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import Base, engine
from routers import complaints, analysis, copilot

load_dotenv()

app = FastAPI(
    title="AIVOA - AI-Powered Customer Complaint Management System",
    description=(
        "Customer Complaint module of a pharmaceutical QMS (API/FDF manufacturing): "
        "structured intake + a LangGraph pipeline of Groq-hosted LLM tools for "
        "summarization, completeness checking, risk classification, duplicate "
        "detection, root-cause hypothesis generation, and CAPA drafting."
    ),
    version="0.1.0",
)

origins = [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)
app.include_router(analysis.router)
app.include_router(copilot.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "ok"}
