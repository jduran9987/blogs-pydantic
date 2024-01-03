# Pydantic for Data Engineers.

Below is a quick guide on using Pydantic within your data pipelines. We create a fake API response (NBA player data) and validate it using Pydantic models. 

## V1 - Data type  Validation.
First, we need a contract. Pretend the following spec tells us what to expect from some API response.

```javascript
# Data about NBA players.

id: int,
name: str,
teams: [
    {
        name: str,
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

Before we move on to more complicated examples, let's break validation by introducing a value to the `last_updated` field that cannot be coerced into a datetime object.

In the `blogs_pydantic/v1_data_type_validation.py` script, change the `last_updated` field on line 53 to the string `"this cannot be coerced into a datetime object"` and then re-run the script.

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
Let's now enforce the following constraints on our fields...
- `id`: positive integers.
- `teams.name`: Upper case strings only.
- `teams.championships`: years older than `1949` are NOT allowed.
- `career_stats`: `ppg`, `rpg`, and `apg` are ALL non-negative floats.
- `dob`: dates older than `1900-01-01` are NOT allowed.
- `draft_year`: years older than `1949` are NOT allowed.
- `positions_played`: `C`, `F`, `G` are the only allowed string values.

Spend some time reading the `pydantic` docs and see if you can figure out how to implement the above constraints to our models. Use the previous `python3 blogs_pydantic/v1_basic_validation.py` script for testing.

Here's one way to apply the above constraints.
```python

...

from typing_extensions import Annotated, Literal

from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    PositiveInt,
    field_validator
)

...

# Change team name to upper case string.
schema = {
    ...

    "teams": [
        {
            "name": "SAN ANTONIO SPURS",
            ...
        }
    ]
}

...

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
            if not name.isupper():
                raise ValueError("Team name must be upper case.")

        return value


class CareerStats(BaseModel):
    ppg: NonNegativeFloat
    rpg: NonNegativeFloat
    apg: NonNegativeFloat


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

    @field_validator("name")
    @classmethod
    def validate_capitalized_names(cls, value):
        names = value.split(" ")

        for name in names:
            if not name[0].isupper():
                raise ValueError("Player names must be capitalized.")

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

"""
Output

{
    'id': 1,
    'name': 'Tim Duncan',
    'teams': [
        {
            'name': 'SAN ANTONIO SPURS',
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

The above implementation contains a few interesting techniques.

**Custom Types**

We create two custom types to keep things DRY. 
- `FirstYearInt` is an integer type greater than or equal to the year 1949. This is the year the NBA was founded.
- `PositionsEnum` is a literal type that only accepts `C, F, G` as values.

**Pydantic Types**

Pydantic offers a suite of prebuilt types that enforce common constraints. We use the `PositiveInt` and `NonNegativeFloat` for the `id` and `career_stats.*` fields.

**Field Validation**

We can use the `field_validator` class method to apply complex validation on fields. We pass in the Pydantic model and field value to validate into the method, and return the validated value or raise an error if validation fails. We use the `field_validator` to validate the `dob`, `name`, and `teams.name` fields.

Once again, let's break validation by setting the `dob` field to a date prior to 1900-01-01.

```python

...

# Set the dob field to 1800-01-01
schema = {
    ...
    "dob": "1800-01-01",
    ...
}

...

if __name__ == "__main__":
    player = Player(**schema)

    print(player.model_dump())

"""
Output

...

pydantic_core._pydantic_core.ValidationError: 1 validation error for Player
dob
  Value error, Years prior to 1900 not allowed. [type=value_error, input_value='1800-01-01', input_type=str]
    For further information visit https://errors.pydantic.dev/2.5/v/value_error
"""
```

Use the `blogs_pydantic/v2_semantic_validation.py` script to test other ways of breaking validation.

## V3 - Schema Validation

There will be times when data producers change our data sources' schema. Whether it be the addition or removal of a column, we'll need a way to handle these changes gracefully within our pipelines.

### Extra fields
By default, Pydantic ignores any newly added columns. Let's verify this behavior by adding a new field `height` to our API response…

```python
...

# Add new field called height.
schema = {
    ...
    "height": "6 feet 11 inches",
    ...
}

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
            'name': 'SAN ANTONIO SPURS',
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

The output completely ignores the new field, and validation passes.
 
The downside of this behavior is that the pipeline dismisses additional fields that could add business value. A better approach is to detect additional fields and log them appropriately. We do this by configuring Pydantic to "allow" fields not defined in our models.

```python
...

import logging

...

if __name__ == "__main__":
    player = Player(**schema)

    print(player.model_dump())

    new_cols = player.model_extra

    # Log new columns
    if new_cols:
        for col in new_cols.keys():
            print(f"New column detected: {col}")
            logging.warn(f"New column detected: {col}")

"""
Output

{
    'id': 1,
    'name': 'Tim Duncan',
    'teams': [
        {
            'name': 'SAN ANTONIO SPURS',
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

New column detected: height
"""
```

### Non-required fields
Fields defined in Pydantic models can be set to optional and nullable. The following guide shows how to do so.
- `field: str` <- Required, cannot be `None`.
- `field: str = None` <- Not required, defaults to `None` if missing.
- `field: str | None` <- Required, can be `None`.
- `field: str | None = None` <- Not required, can be `None`, defaults to `None`.

This is useful when the data producer does not guarantee the delivery of a given field.

```python
...

# Remove dob and change last_updated to None
schema = {
    ...
    # "dob": "1976-04-25"
    ...
    "last_updated": None
}

...

class Player(BaseModel):
    ...

    dob: date = None
    ...
    last_updated: datetime | None

...

if __name__ == "__main__":
    player = Player(**schema)

    print(player.model_dump())

    new_cols = player.model_extra

    # Log new columns
    if new_cols:
        for col in new_cols.keys():
            print(f"New column detected: {col}")
            logging.warn(f"New column detected: {col}")

"""
Output

{
    'id': 1,
    'name': 'Tim Duncan',
    'teams': [
        {
            'name': 'SAN ANTONIO SPURS',
            'championships': [1999, 2003, 2005, 2007, 2014]
        }
    ],
    'career_stats': {
        'ppg': 19.0,
        'rpg': 10.8,
        'apg': 3.0
    },
    'dob': None,
    'draft_year': 1997,
    'positions_played': ['F', 'C'],
    'is_active': False,
    'last_updated': None
}

New column detected: height
"""
```

We removed the `dob` field in the above example, yet it still passed validation. The field appeared in our data as its default value `None`.

Use the code in `blogs_pydantic/v3_schema_validation.py` to test out more schema changes.
