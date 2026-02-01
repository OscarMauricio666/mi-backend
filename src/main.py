"""
Mi Backend API - Main Application.

REST API built with FastAPI, MongoDB Atlas, and external APIs.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import connect_to_mongo, close_mongo_connection
from src.routes.claude import router as claude_router
from src.routes.crypto import router as crypto_router
from src.routes.news import router as news_router
from src.routes.sports import router as sports_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Mi Backend API

REST API with multiple external service integrations.

### Services

* **Claude AI**: Chat with Anthropic's Claude
* **Crypto**: Bitcoin and cryptocurrency prices (CoinGecko)
* **News**: Top headlines and articles (NewsAPI)
* **Sports**: Football matches and standings (API-Football)

### Database

* **MongoDB Atlas**: Cloud database with Beanie ODM

### Documentation

* [Swagger UI](/docs)
* [ReDoc](/redoc)
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(claude_router, prefix="/api/v1")
app.include_router(crypto_router, prefix="/api/v1")
app.include_router(news_router, prefix="/api/v1")
app.include_router(sports_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Welcome to Mi Backend API",
        "version": settings.app_version,
        "docs": "/docs",
        "services": ["claude", "crypto", "news", "sports"]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Check API status."""
    from src.database import db
    return {
        "status": "ok",
        "mongodb": "connected" if db.connected else "disconnected"
    }
