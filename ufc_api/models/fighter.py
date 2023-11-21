from datetime import datetime
from typing import Optional

from pydantic import root_validator
from sqlmodel import Field
from sqlmodel import SQLModel

# TODO: Add field for dateOfBirth


class FighterCreate(SQLModel):
    first_name: Optional[str] = Field(default=None, alias="firstName", description="First name", min_length=1)
    last_name: Optional[str] = Field(default=None, alias="lastName", description="Last name", min_length=1)
    nickname: Optional[str] = Field(default=None, description="Nickname", min_length=1)

    height: Optional[int] = Field(default=None, description="Height (in)", gt=0)
    weight: Optional[int] = Field(default=None, description="Weight (lbs)", gt=0)
    reach: Optional[int] = Field(default=None, description="Reach (in)", gt=0)
    stance: Optional[str] = Field(default=None, description="Stance", min_length=1)

    wins: int = Field(description="Number of wins", ge=0)
    losses: int = Field(description="Number of losses", ge=0)
    draws: int = Field(description="Number of draws", ge=0)
    no_contests: int = Field(alias="noContests", description="Number of no contests", ge=0)
    current_champion: bool = Field(
        alias="currentChampion",
        description="Is the fighter currently a champion?",
    )

    slpm: Optional[float] = Field(default=None, description="Significant strikes landed per minute", ge=0.0)
    str_acc: Optional[float] = Field(
        default=None,
        alias="strAcc",
        description="Significant striking accuracy",
        ge=0.0,
    )
    sapm: Optional[float] = Field(default=None, description="Significant strikes absorbed per minute", ge=0.0)
    str_def: Optional[float] = Field(
        default=None,
        alias="strDef",
        description="Significant strike defense",
        ge=0.0,
    )
    td_avg: Optional[float] = Field(
        default=None,
        alias="tdAvg",
        description="Average takedowns landed per 15 minutes",
        ge=0.0,
    )
    td_acc: Optional[float] = Field(default=None, alias="tdAcc", description="Takedown accuracy", ge=0.0)
    td_def: Optional[float] = Field(default=None, alias="tdDef", description="Takedown defense", ge=0.0)
    sub_avg: Optional[float] = Field(
        default=None,
        alias="subAvg",
        description="Average submissions attempted per 15 minutes",
        ge=0.0,
    )

    @root_validator
    def check_fighter_name(cls, values: dict) -> dict:
        first_name = values.get("first_name")
        if not isinstance(first_name, str):
            first_name = ""

        last_name = values.get("last_name")
        if not isinstance(last_name, str):
            last_name = ""

        full_name = (first_name + " " + last_name).strip()
        if full_name == "":
            raise ValueError("fighter has no name")

        return values


class Fighter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    first_name: Optional[str] = Field(alias="firstName", index=True)
    last_name: Optional[str] = Field(alias="lastName", index=True)
    nickname: Optional[str] = Field(index=True)

    height: Optional[int]
    weight: Optional[int]
    reach: Optional[int]
    stance_id: Optional[int] = Field(default=None, foreign_key="stance.id")

    wins: int = Field(nullable=False)
    losses: int = Field(nullable=False)
    draws: int = Field(nullable=False)
    no_contests: int = Field(nullable=False, alias="noContests")
    current_champion: bool = Field(nullable=False, alias="currentChampion")

    slpm: Optional[float]
    str_acc: Optional[float] = Field(alias="strAcc")
    sapm: Optional[float]
    str_def: Optional[float] = Field(alias="strDef")
    td_avg: Optional[float] = Field(alias="tdAvg")
    td_acc: Optional[float] = Field(alias="tdAcc")
    td_def: Optional[float] = Field(alias="tdDef")
    sub_avg: Optional[float] = Field(alias="subAvg")


class FighterReadSimple(SQLModel):
    id: int = Field(description="ID")
    created_at: datetime = Field(alias="createdAt", description="Date and time of creation")
    full_name: str = Field(alias="fullName", description="Full name")

    @classmethod
    def from_db_obj(cls, db_fighter: Fighter) -> "FighterReadSimple":
        first_name = db_fighter.first_name
        if not isinstance(first_name, str):
            first_name = ""

        last_name = db_fighter.last_name
        if not isinstance(last_name, str):
            last_name = ""

        data_dict = {
            "id": db_fighter.id,
            "createdAt": db_fighter.created_at,
            "fullName": (first_name + " " + last_name).strip(),
        }
        return cls.parse_obj(data_dict)
