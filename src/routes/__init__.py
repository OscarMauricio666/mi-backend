"""
API Routes.

This module contains endpoints organized by resource.
"""

from src.routes.claude import router as claude_router
from src.routes.crypto import router as crypto_router
from src.routes.news import router as news_router
from src.routes.sports import router as sports_router
