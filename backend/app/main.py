from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .config import settings
from .db import criar_tabelas
from .rotas import bases, incidentes, webhooks

@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield

app = FastAPI(title="Canário", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bases.router)
app.include_router(incidentes.router)
app.include_router(webhooks.router)

@app.get("/saude", tags=["infra"])
def saude():
    return {"status": "ok"}

