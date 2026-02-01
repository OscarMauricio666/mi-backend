"""
News Document for MongoDB.

Stores news articles from NewsAPI.
"""

from datetime import datetime, timezone
from typing import Optional
from beanie import Document
from pydantic import Field


class NewsArticle(Document):
    """News article document."""

    source_name: str = Field(..., description="News source name")
    author: Optional[str] = Field(None, description="Article author")
    title: str = Field(..., description="Article title")
    description: Optional[str] = Field(None, description="Article description")
    url: str = Field(..., description="Article URL")
    image_url: Optional[str] = Field(None, description="Article image URL")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    category: Optional[str] = Field(None, description="News category")
    country: Optional[str] = Field(None, description="News country")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "news_articles"
        indexes = [
            "title",
            "category",
            "country",
        ]
