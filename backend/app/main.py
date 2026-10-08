from fastapi import FastAPI

from app.database.base import Base
from app.database.connection import engine

from app.models.user import User
from app.models.case import Case
from app.models.document import Document

from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.ask import router as ask_router
from app.routes.cases import router as cases_router
from app.routes.documents import router as documents_router


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="DigiLaw API",
    description="AI-powered legal assistance backend",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware
import os

allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTES
# =========================================================

app.include_router(
    health_router,
    prefix="/api"
)

app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Auth"]
)

app.include_router(
    ask_router,
    prefix="/api"
)

app.include_router(
    cases_router,
    prefix="/api"
)

app.include_router(
    documents_router,
    prefix="/api"
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "DigiLaw Backend is running 🚀"
    }