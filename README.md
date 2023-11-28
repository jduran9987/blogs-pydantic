# Pydantic for Data Engineers.

## V1 - Basic Validation.
First, we need a contract. Pretend the following spec tells us what we should expect from some API response.

```javascript
# Data about NBA players.

id: int,
name: str,
teams: [
    {
        name:str,
        years: list[int]
    }
],
career_stats: {
    ppg: float,
    rpg: float,
    apg: float
},
dob: date,
draft_year: int,
positions_played: list[str],
is_active: bool,
last_updated: datetime
```

Let's create a fake API response and use `pydantic` to validate the data types.

```python
from datetime import date, datetime

from pydantic import BaseModel

# Sample API response
schema = {
    "id": 1,
    "name": "Tim Duncan",
    "teams": [
        {
            "name": "San Antonio Sputs",
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

"""
Output

{
    'id': 1,
    'name': 'Tim Duncan',
    'teams': [
        {
            'name': 'San Antonio Spurs',
            'championships': [1999, 2003, 2005, 2007, 2014]
        }
    ],
    'career_stats': {
        'ppg': 19.0,
        'rpg': 10.8,
        'apg': 3.0
    },
    'dob': datetime.date(1976, 4, 25),
    'draft_year': 1997,
    'positions_played': ['F', 'C'],
    'is_active': False,
    'last_updated': datetime.datetime(2023, 10, 10, 0, 0)
}
"""
```

Run the `python3 blogs_pydantic/v1_basic_validation.py` script.

A few noteworthy things are happening in the above script...

- Each `pydantic` model is simply a Python class that inherits from `BaseModel`.
- One class/model is created per nested object (in the API response) and referenced in the parent class.
- JSON data types are limited. If possible, they will be coerced into the data types specified in the `pydantic` model. Otherwise, validation fails.

Before we move onto more complicated examples, let's break validation by introducing a value to the `last_updated` field that cannot be coerced into a datetime object.

In the `python3 blogs_pydantic/v1_basic_validation.py` script, change the `last_updated` field on line 53 to the string `"this cannot be coerced into a datetime object"` then re-run the script.

```python
from datetime import date, datetime

...

# Sample API response
schema = {
    ...
    "last_updated": "This cannot be coerced into a datetime object"
}

...

class Player(BaseModel):
    ...
    last_updated: datetime


if __name__ == "__main__":
    player = Player(**schema)

    print(player.model_dump())

"""
Output

...

pydantic_core._pydantic_core.ValidationError: 1 validation error for Player
last_updated
  Input should be a valid datetime, invalid character in year [type=datetime_parsing, input_value='This cannot be coerced into a datetime object', input_type=str]
    For further information visit https://errors.pydantic.dev/2.5/v/datetime_parsing
"""
```

Validation fails as expected. Feel free to play around with other fields and data types.

## V2 - Semantic & format validation.
We now want to enforce the following formatting and value constraints on our fields...
- `id`: positive integers.
- `name`: capitalized first and last names.
- `teams.name`: capitalized words.
- `teams.championships`: years older than `1949` are NOT allowed.
- `career_stats`: `ppg`, `rpg`, and `apg` are ALL non-negative floats.
- `dob`: dates older than `1900-01-01` are NOT allowed.
- `draft_year`: years older than `1949` are NOT allowed.
- `positions_played`: `C`, `F`, `G` are the only allowed string values.

Spend some time reading the `pydantic` docs and see if you can figure out how to implement the above constraints to our models. Use the previous `python3 blogs_pydantic/v1_basic_validation.py` script for testing.

Here's one way to apply the above constraints.
```python
...

from typing_extensions import Literal

from pydantic import BaseModel, Field

...

# Custom types
FirstYearInt = Annotated[int, Field(ge=1949)]
PositionsEnum = Literal["C", "F", "G"]

# Pydantic models
class Teams(BaseModel):
    name: str
    championships: list[FirstYearInt]


class CareerStats(BaseModel):
    ppg: float = Field(ge=0)
    rpg: float = Field(ge=0)
    apg: float = Field(ge=0)


class Player(BaseModel):
    id: int = Field(ge=1)
    name: str
    teams: list[Teams]
    career_stats: CareerStats
    dob: date
    draft_year: FirstYearInt
    positions_played: list[PositionsEnum]
    is_active: bool
    last_updated: datetime


if __name__ == "__main__":
    player = Player(**schema)

    print(player.model_dump())
```
