"""
Sports Document for MongoDB.

Stores football data from API-Football.
"""

from datetime import datetime, timezone
from typing import Optional, List
from beanie import Document
from pydantic import Field


class FootballMatch(Document):
    """Football match document."""

    fixture_id: int = Field(..., description="Fixture ID from API")
    league_id: int = Field(..., description="League ID")
    league_name: str = Field(..., description="League name")
    league_country: str = Field(..., description="League country")
    home_team: str = Field(..., description="Home team name")
    away_team: str = Field(..., description="Away team name")
    home_score: Optional[int] = Field(None, description="Home team score")
    away_score: Optional[int] = Field(None, description="Away team score")
    status: str = Field(..., description="Match status")
    match_date: datetime = Field(..., description="Match date and time")
    venue: Optional[str] = Field(None, description="Match venue")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "football_matches"
        indexes = [
            "fixture_id",
            "league_id",
            "match_date",
        ]


class FootballTeam(Document):
    """Football team document."""

    team_id: int = Field(..., description="Team ID from API")
    name: str = Field(..., description="Team name")
    code: Optional[str] = Field(None, description="Team code")
    country: str = Field(..., description="Team country")
    logo_url: Optional[str] = Field(None, description="Team logo URL")
    venue_name: Optional[str] = Field(None, description="Home venue name")
    venue_capacity: Optional[int] = Field(None, description="Venue capacity")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "football_teams"
        indexes = [
            "team_id",
            "name",
        ]
