"""
News Service.

Fetches news from NewsAPI and stores in MongoDB.
"""

from typing import List, Optional
from datetime import datetime, timezone
import httpx

from src.config import get_settings
from src.documents.news import NewsArticle

settings = get_settings()

NEWSAPI_BASE_URL = "https://newsapi.org/v2"


class NewsService:
    """Service for news data from NewsAPI."""

    def __init__(self):
        """Initialize HTTP client."""
        self.client = httpx.AsyncClient(timeout=30.0)
        self.api_key = settings.newsapi_key

    async def get_top_headlines(
        self,
        country: str = "us",
        category: str = None,
        query: str = None,
        page_size: int = 10
    ) -> dict:
        """
        Fetch top headlines from NewsAPI.

        Args:
            country: Country code (us, mx, ar, etc.)
            category: Category (business, technology, sports, etc.)
            query: Search query
            page_size: Number of results

        Returns:
            NewsAPI response
        """
        if not self.api_key or self.api_key == "tu-newsapi-key":
            raise ValueError("NEWSAPI_KEY not configured. Update your .env file")

        url = f"{NEWSAPI_BASE_URL}/top-headlines"
        params = {
            "apiKey": self.api_key,
            "country": country,
            "pageSize": page_size
        }

        if category:
            params["category"] = category
        if query:
            params["q"] = query

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def fetch_and_store(
        self,
        country: str = "us",
        category: str = None,
        page_size: int = 10
    ) -> List[NewsArticle]:
        """
        Fetch news and store in MongoDB.

        Args:
            country: Country code
            category: News category
            page_size: Number of articles

        Returns:
            List of stored NewsArticle documents
        """
        data = await self.get_top_headlines(country, category, page_size=page_size)
        stored = []

        for article in data.get("articles", []):
            # Parse published date
            published_at = None
            if article.get("publishedAt"):
                try:
                    published_at = datetime.fromisoformat(
                        article["publishedAt"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            news = NewsArticle(
                source_name=article.get("source", {}).get("name", "Unknown"),
                author=article.get("author"),
                title=article.get("title", ""),
                description=article.get("description"),
                url=article.get("url", ""),
                image_url=article.get("urlToImage"),
                published_at=published_at,
                category=category,
                country=country
            )
            await news.insert()
            stored.append(news)

        return stored

    async def get_latest(self, limit: int = 10, category: str = None) -> List[NewsArticle]:
        """
        Get latest stored news.

        Args:
            limit: Max records
            category: Filter by category

        Returns:
            List of NewsArticle documents
        """
        query = NewsArticle.find()
        if category:
            query = NewsArticle.find(NewsArticle.category == category)

        return await query.sort("-created_at").limit(limit).to_list()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
