"""
MongoDB Documents (ODM with Beanie).

This module contains document models for MongoDB collections.
"""

from src.documents.crypto import CryptoPrice
from src.documents.news import NewsArticle
from src.documents.sports import FootballMatch, FootballTeam

# All document models for Beanie initialization
ALL_DOCUMENTS = [
    CryptoPrice,
    NewsArticle,
    FootballMatch,
    FootballTeam,
]
