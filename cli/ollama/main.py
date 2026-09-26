import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

from luminary.model.application.services.ollama_service import IOllamaService
from luminary.model.infrastructure.services.llama_index.client import MappedOpenAI
from luminary.model.infrastructure.services.llama_index.ollama_service import (
    LlamaIndexOllamaServiceImpl,
)
from luminary.model.presentation.ollama.fastapi.ollama_controllers import ollama_router


load_dotenv()
logger = logging.getLogger("luminary-ollama")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-REPLACE")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")


# Database and dependency setup
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application...")

    llm = MappedOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        api_base=OPENAI_BASE_URL,
        temperature=0,
    )
    embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY, api_base=OPENAI_BASE_URL)

    # Initialize dependencies
    Settings.llm = llm
    Settings.embed_model = embed_model

    # Repositories
    ollama_service = LlamaIndexOllamaServiceImpl(llm, OPENAI_MODEL)

    # Dependency overrides
    app.dependency_overrides[IOllamaService] = lambda: ollama_service

    yield

    # Cleanup
    logger.info("Shutting down application...")


# FastAPI app
app = FastAPI(
    title="Luminary Ollama API",
    description="API for proxying Ollama requests to Luminary internals",
    version="0.0.0",
    lifespan=lifespan,
)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers
app.include_router(ollama_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
