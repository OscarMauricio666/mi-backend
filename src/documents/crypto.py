"""
Crypto Document for MongoDB.

Stores cryptocurrency price data from CoinGecko.
"""

from datetime import datetime, timezone
from typing import Optional
from beanie import Document
from pydantic import Field


class CryptoPrice(Document):
    """Cryptocurrency price document."""

    coin_id: str = Field(..., description="Coin identifier (e.g., 'bitcoin')")
    symbol: str = Field(..., description="Coin symbol (e.g., 'btc')")
    name: str = Field(..., description="Coin name (e.g., 'Bitcoin')")
    current_price_usd: float = Field(..., description="Current price in USD")
    market_cap_usd: Optional[float] = Field(None, description="Market cap in USD")
    price_change_24h: Optional[float] = Field(None, description="24h price change percentage")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "crypto_prices"
        indexes = [
            "coin_id",
            "symbol",
        ]
