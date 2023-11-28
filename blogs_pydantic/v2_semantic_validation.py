"""
V1 - Basic validation.

Validate basic data types. Feel free to play around with the data types
defined in the pydantic models.
"""

from datetime import date, datetime
from typing_extensions import Annotated, Literal

from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    PositiveInt,
    field_validator
)

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

# Custom types
FirstYearInt = Annotated[int, Field(ge=1949)]
PositionsEnum = Literal["C", "F", "G"]


# Pydantic models
class Teams(BaseModel):
    name: str
    championships: list[FirstYearInt]

    @field_validator("name")
    @classmethod
    def validate_upper_case_names(cls, value):
        names = value.split(" ")

        for name in names:
            if not name[0].isupper():
                raise ValueError("Team name  must be capitalized.")

        return value


class CareerStats(BaseModel):
    ppg: NonNegativeFloat
    rpg: NonNegativeFloat
    apg: NonNegativeFloat


class Player(BaseModel):
    id: PositiveInt
    name: str
    teams: list[Teams]
    career_stats: CareerStats
    dob: date
    draft_year: FirstYearInt
    position_played: list[PositionsEnum]
    is_active: bool
    last_updated: datetime

    @field_validator("name")
    @classmethod
    def validate_upper_case_names(cls, value):
        names = value.split(" ")

        for name in names:
            if not name[0].isupper():
                raise ValueError("Names must be capitalized.")

        return value

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value):
        if value < date(1900, 1, 1):
            raise ValueError("Years prior to 1900 not allowed.")

        return value


if __name__ == "__main__":
    player = Player(**schema)

    print(player.model_dump())
