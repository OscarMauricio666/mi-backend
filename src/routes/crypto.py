"""
Crypto routes.

Endpoints for cryptocurrency data.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from src.services.crypto_service import CryptoService
from src.database import db

router = APIRouter(prefix="/crypto", tags=["Crypto"])


@router.get(
    "/prices",
    summary="Get crypto prices",
    description="Fetch current prices from CoinGecko (does not store)."
)
async def get_prices(
    coins: str = Query("bitcoin,ethereum", description="Comma-separated coin IDs")
):
    """
    Get current cryptocurrency prices from CoinGecko.

    - **coins**: Comma-separated list of coin IDs (e.g., bitcoin,ethereum,solana)
    """
    service = CryptoService()
    try:
        coin_list = [c.strip() for c in coins.split(",")]
        data = await service.get_prices(coin_list)
        return {"prices": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching prices: {str(e)}"
        )
    finally:
        await service.close()


@router.post(
    "/fetch",
    summary="Fetch and store prices",
    description="Fetch prices from CoinGecko and store in MongoDB."
)
async def fetch_and_store(
    coins: str = Query("bitcoin,ethereum", description="Comma-separated coin IDs")
):
    """
    Fetch cryptocurrency prices and store in database.

    Requires MongoDB connection.
    """
    if not db.connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB not connected. Configure MONGODB_URL in .env"
        )

    service = CryptoService()
    try:
        coin_list = [c.strip() for c in coins.split(",")]
        stored = await service.fetch_and_store(coin_list)
        return {
            "message": f"Stored {len(stored)} price records",
            "data": [{"coin": p.name, "price": p.current_price_usd} for p in stored]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing prices: {str(e)}"
        )
    finally:
        await service.close()


@router.get(
    "/history/{coin_id}",
    summary="Get price history",
    description="Get stored price history for a coin."
)
async def get_history(coin_id: str, limit: int = Query(10, ge=1, le=100)):
    """
    Get price history from database.

    - **coin_id**: Coin identifier (e.g., bitcoin)
    - **limit**: Max records to return
    """
    if not db.connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB not connected"
        )

    service = CryptoService()
    try:
        history = await service.get_history(coin_id, limit)
        return {
            "coin_id": coin_id,
            "count": len(history),
            "history": [
                {
                    "price": h.current_price_usd,
                    "change_24h": h.price_change_24h,
                    "timestamp": h.last_updated
                }
                for h in history
            ]
        }
    finally:
        await service.close()
