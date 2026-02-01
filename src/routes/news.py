"""
News routes.

Endpoints for news data.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from src.services.news_service import NewsService
from src.database import db

router = APIRouter(prefix="/news", tags=["News"])


@router.get(
    "/headlines",
    summary="Get top headlines",
    description="Fetch top headlines from NewsAPI (does not store)."
)
async def get_headlines(
    country: str = Query("us", description="Country code (us, mx, ar, co, etc.)"),
    category: Optional[str] = Query(None, description="Category: business, technology, sports, entertainment, health, science"),
    query: Optional[str] = Query(None, description="Search query"),
    page_size: int = Query(10, ge=1, le=100)
):
    """
    Get top headlines from NewsAPI.

    - **country**: ISO country code
    - **category**: News category filter
    - **query**: Search term
    """
    service = NewsService()
    try:
        data = await service.get_top_headlines(country, category, query, page_size)
        return data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching news: {str(e)}"
        )
    finally:
        await service.close()


@router.post(
    "/fetch",
    summary="Fetch and store news",
    description="Fetch headlines from NewsAPI and store in MongoDB."
)
async def fetch_and_store(
    country: str = Query("us", description="Country code"),
    category: Optional[str] = Query(None, description="News category"),
    page_size: int = Query(10, ge=1, le=100)
):
    """
    Fetch news and store in database.

    Requires MongoDB connection and NewsAPI key.
    """
    if not db.connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB not connected. Configure MONGODB_URL in .env"
        )

    service = NewsService()
    try:
        stored = await service.fetch_and_store(country, category, page_size)
        return {
            "message": f"Stored {len(stored)} articles",
            "articles": [{"title": a.title, "source": a.source_name} for a in stored]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing news: {str(e)}"
        )
    finally:
        await service.close()


@router.get(
    "/stored",
    summary="Get stored news",
    description="Get news articles from database."
)
async def get_stored(
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None)
):
    """
    Get stored news from database.

    - **limit**: Max articles to return
    - **category**: Filter by category
    """
    if not db.connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB not connected"
        )

    service = NewsService()
    try:
        articles = await service.get_latest(limit, category)
        return {
            "count": len(articles),
            "articles": [
                {
                    "title": a.title,
                    "source": a.source_name,
                    "description": a.description,
                    "url": a.url,
                    "published_at": a.published_at
                }
                for a in articles
            ]
        }
    finally:
        await service.close()
