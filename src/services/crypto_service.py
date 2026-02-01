"""
Crypto Service.

Fetches cryptocurrency data from CoinGecko API and stores in MongoDB.
"""

from typing import List, Optional
from datetime import datetime, timezone
import httpx

from src.documents.crypto import CryptoPrice

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


class CryptoService:
    """Service for cryptocurrency data from CoinGecko."""

    def __init__(self):
        """Initialize HTTP client."""
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_prices(self, coins: List[str] = None) -> List[dict]:
        """
        Fetch current prices for cryptocurrencies.

        Args:
            coins: List of coin IDs (default: bitcoin, ethereum)

        Returns:
            List of price data
        """
        if coins is None:
            coins = ["bitcoin", "ethereum"]

        ids = ",".join(coins)
        url = f"{COINGECKO_BASE_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": ids,
            "order": "market_cap_desc",
            "sparkline": "false",
            "price_change_percentage": "24h"
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def fetch_and_store(self, coins: List[str] = None) -> List[CryptoPrice]:
        """
        Fetch prices from CoinGecko and store in MongoDB.

        Args:
            coins: List of coin IDs to fetch

        Returns:
            List of stored CryptoPrice documents
        """
        data = await self.get_prices(coins)
        stored = []

        for coin in data:
            crypto = CryptoPrice(
                coin_id=coin["id"],
                symbol=coin["symbol"],
                name=coin["name"],
                current_price_usd=coin["current_price"],
                market_cap_usd=coin.get("market_cap"),
                price_change_24h=coin.get("price_change_percentage_24h"),
                last_updated=datetime.now(timezone.utc)
            )
            await crypto.insert()
            stored.append(crypto)

        return stored

    async def get_latest(self, coin_id: str) -> Optional[CryptoPrice]:
        """
        Get latest stored price for a coin.

        Args:
            coin_id: Coin identifier

        Returns:
            Latest CryptoPrice or None
        """
        return await CryptoPrice.find_one(
            CryptoPrice.coin_id == coin_id,
            sort=[("last_updated", -1)]
        )

    async def get_history(self, coin_id: str, limit: int = 10) -> List[CryptoPrice]:
        """
        Get price history for a coin.

        Args:
            coin_id: Coin identifier
            limit: Max records to return

        Returns:
            List of CryptoPrice documents
        """
        return await CryptoPrice.find(
            CryptoPrice.coin_id == coin_id
        ).sort("-last_updated").limit(limit).to_list()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
