"""
Sports Service.

Fetches football data from API-Football and stores in MongoDB.
"""

from typing import List, Optional
from datetime import datetime, timezone
import httpx

from src.config import get_settings
from src.documents.sports import FootballMatch, FootballTeam

settings = get_settings()

API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"


class SportsService:
    """Service for football data from API-Football."""

    def __init__(self):
        """Initialize HTTP client with API key header."""
        self.api_key = settings.football_api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"x-apisports-key": self.api_key} if self.api_key else {}
        )

    def _check_api_key(self):
        """Validate API key is configured."""
        if not self.api_key or self.api_key == "tu-football-api-key":
            raise ValueError("FOOTBALL_API_KEY not configured. Update your .env file")

    async def get_live_matches(self) -> dict:
        """
        Fetch live football matches.

        Returns:
            API-Football response with live matches
        """
        self._check_api_key()
        url = f"{API_FOOTBALL_BASE_URL}/fixtures"
        params = {"live": "all"}

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_matches_by_date(self, date: str) -> dict:
        """
        Fetch matches for a specific date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            API-Football response
        """
        self._check_api_key()
        url = f"{API_FOOTBALL_BASE_URL}/fixtures"
        params = {"date": date}

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_league_standings(self, league_id: int, season: int) -> dict:
        """
        Fetch league standings.

        Args:
            league_id: League ID
            season: Season year

        Returns:
            API-Football response with standings
        """
        self._check_api_key()
        url = f"{API_FOOTBALL_BASE_URL}/standings"
        params = {"league": league_id, "season": season}

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def fetch_and_store_matches(self, date: str = None) -> List[FootballMatch]:
        """
        Fetch matches and store in MongoDB.

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            List of stored FootballMatch documents
        """
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        data = await self.get_matches_by_date(date)
        stored = []

        for fixture in data.get("response", []):
            fixture_data = fixture.get("fixture", {})
            league_data = fixture.get("league", {})
            teams_data = fixture.get("teams", {})
            goals_data = fixture.get("goals", {})

            # Parse match date
            match_date = datetime.now(timezone.utc)
            if fixture_data.get("date"):
                try:
                    match_date = datetime.fromisoformat(
                        fixture_data["date"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            match = FootballMatch(
                fixture_id=fixture_data.get("id", 0),
                league_id=league_data.get("id", 0),
                league_name=league_data.get("name", "Unknown"),
                league_country=league_data.get("country", "Unknown"),
                home_team=teams_data.get("home", {}).get("name", "Unknown"),
                away_team=teams_data.get("away", {}).get("name", "Unknown"),
                home_score=goals_data.get("home"),
                away_score=goals_data.get("away"),
                status=fixture_data.get("status", {}).get("long", "Unknown"),
                match_date=match_date,
                venue=fixture_data.get("venue", {}).get("name")
            )
            await match.insert()
            stored.append(match)

        return stored

    async def get_stored_matches(
        self,
        limit: int = 10,
        league_id: int = None
    ) -> List[FootballMatch]:
        """
        Get stored matches from MongoDB.

        Args:
            limit: Max records
            league_id: Filter by league

        Returns:
            List of FootballMatch documents
        """
        query = FootballMatch.find()
        if league_id:
            query = FootballMatch.find(FootballMatch.league_id == league_id)

        return await query.sort("-match_date").limit(limit).to_list()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
