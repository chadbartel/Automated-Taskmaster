# Standard Library
from typing import List, Optional, Union

# Third Party
from pydantic import BaseModel, Field


class MonsterSummonRequest(BaseModel):
    """Request model for summoning monsters based on various parameters."""

    cr_min: Optional[float] = Field(
        None, description="Minimum Challenge Rating", ge=0
    )
    cr_max: Optional[float] = Field(
        None, description="Maximum Challenge Rating", ge=0
    )
    environment: Optional[str] = Field(
        None, description="e.g., 'forest', 'cave', 'urban'"
    )
    limit: int = Field(
        10, description="Maximum number of monsters to return", ge=1, le=50
    )


class Monster(BaseModel):
    """Model representing a monster with its attributes."""

    name: str = Field(..., description="Name of the monster")
    cr: Union[float, str] = Field(
        ..., description="Challenge Rating of the monster"
    )
    environment: List[str] = Field(
        ..., description="List of environments the monster can be found in"
    )
    source: str = Field(
        ...,
        description="Source of the monster data, e.g., 'Monster Manual', 'Volo's Guide to Monsters'",
    )


class MonsterSummonResponse(BaseModel):
    """Response model for the monster summon request."""

    query_parameters: MonsterSummonRequest = Field(
        ..., description="Parameters used for the monster summon request"
    )
    summoned_monsters: List[Monster] = Field(
        ..., description="List of summoned monsters"
    )
    count: int = Field(
        ..., description="Total number of monsters returned in the response"
    )
