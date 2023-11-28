"""
V1 - Basic validation.

Validate basic data types. Feel free to play around with the data types
defined in the pydantic models.
"""

from datetime import date, datetime

from pydantic import BaseModel

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
    "dob": "1976-04-25",
    "draft_year": 1997,
    "position_played": ["F", "C"],
    "is_active": False,
    "last_updated": "2023-10-10T00:00:00.0000"
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
    id: int
    name: str
    teams: list[Teams]
    career_stats: CareerStats
    dob: date
    draft_year: int
    positions_played: list[str]
    is_active: bool
    last_updated: datetime


if __name__ == "__main__":
    player = Player(**schema)

    print(player.model_dump())
