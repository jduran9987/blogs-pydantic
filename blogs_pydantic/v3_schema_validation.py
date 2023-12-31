"""
V3 - Schema validation.

Validate basic data types. Feel free to play around with the data types
defined in the pydantic models.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

# Sample API response
schema = {
    "id": 1,
    "name": "Tim Duncan",
    "teams": [
        {
            "name": "San Antonio Spurs",
            "championships": [1999, 2003, 2005, 2007, 2014]
        }
    ],
    "career_stats": {
        "ppg": 19.0,
        "rpg": 10.8,
        "apg": 3.0
    },
    # "dob": "1976-04-25",
    "height": "6 feet 11 inches",
    "draft_year": 1997,
    "positions_played": ["F", "C"],
    "is_active": False,
    "last_updated": None
}


# Pydantic models
class Teams(BaseModel):
    name: str
    championships: list[int]


class CareerStats(BaseModel):
    ppg: float
    rpg: float
    apg: float


class Player(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    teams: list[Teams]
    career_stats: CareerStats
    dob: date = None
    draft_year: int
    positions_played: list[str]
    is_active: bool
    last_updated: datetime | None


if __name__ == "__main__":
    player = Player(**schema)

    print(player.model_dump())

    new_cols = player.model_extra

    if new_cols:
        for col in new_cols.keys():
            print(f"New column detected: {col}")
