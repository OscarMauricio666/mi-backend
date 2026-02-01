"""
Sports routes.

Endpoints for football/sports data.
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Query

from src.services.sports_service import SportsService
from src.database import db

router = APIRouter(prefix="/sports", tags=["Sports"])


@router.get(
    "/football/live",
    summary="Get live matches",
    description="Fetch live football matches from API-Football."
)
async def get_live_matches():
    """Get currently live football matches."""
    service = SportsService()
    try:
        data = await service.get_live_matches()
        return data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching live matches: {str(e)}"
        )
    finally:
        await service.close()


@router.get(
    "/football/matches",
    summary="Get matches by date",
    description="Fetch football matches for a specific date."
)
async def get_matches_by_date(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (default: today)")
):
    """
    Get football matches for a date.

    - **date**: Date in YYYY-MM-DD format
    """
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    service = SportsService()
    try:
        data = await service.get_matches_by_date(date)
        return data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching matches: {str(e)}"
        )
    finally:
        await service.close()


@router.get(
    "/football/standings",
    summary="Get league standings",
    description="Fetch standings for a football league."
)
async def get_standings(
    league_id: int = Query(..., description="League ID (e.g., 39 for Premier League)"),
    season: int = Query(2024, description="Season year")
):
    """
    Get league standings.

    Popular league IDs:
    - 39: Premier League
    - 140: La Liga
    - 135: Serie A
    - 78: Bundesliga
    - 61: Ligue 1
    """
    service = SportsService()
    try:
        data = await service.get_league_standings(league_id, season)
        return data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching standings: {str(e)}"
        )
    finally:
        await service.close()


@router.post(
    "/football/fetch",
    summary="Fetch and store matches",
    description="Fetch matches and store in MongoDB."
)
async def fetch_and_store(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """
    Fetch matches and store in database.

    Requires MongoDB connection and API-Football key.
    """
    if not db.connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB not connected. Configure MONGODB_URL in .env"
        )

    service = SportsService()
    try:
        stored = await service.fetch_and_store_matches(date)
        return {
            "message": f"Stored {len(stored)} matches",
            "matches": [
                {
                    "home": m.home_team,
                    "away": m.away_team,
                    "league": m.league_name,
                    "status": m.status
                }
                for m in stored[:10]  # Limit response
            ]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing matches: {str(e)}"
        )
    finally:
        await service.close()


@router.get(
    "/football/stored",
    summary="Get stored matches",
    description="Get matches from database."
)
async def get_stored_matches(
    limit: int = Query(10, ge=1, le=100),
    league_id: Optional[int] = Query(None, description="Filter by league ID")
):
    """
    Get stored matches from database.

    - **limit**: Max matches to return
    - **league_id**: Filter by league
    """
    if not db.connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB not connected"
        )

    service = SportsService()
    try:
        matches = await service.get_stored_matches(limit, league_id)
        return {
            "count": len(matches),
            "matches": [
                {
                    "home": m.home_team,
                    "away": m.away_team,
                    "home_score": m.home_score,
                    "away_score": m.away_score,
                    "league": m.league_name,
                    "status": m.status,
                    "date": m.match_date
                }
                for m in matches
            ]
        }
    finally:
        await service.close()
