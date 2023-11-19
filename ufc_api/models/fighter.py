from datetime import datetime
from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class Fighter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    first_name: Optional[str] = Field(
        default=None,
        alias="firstName",
        title="First name",
        min_length=1,
        description="First name cannot be an empty string",
        index=True,
    )
    last_name: Optional[str] = Field(
        default=None,
        alias="lastName",
        title="Last name",
        min_length=1,
        description="Last name cannot be an empty string",
        index=True,
    )
    nickname: Optional[str] = Field(
        default=None,
        title="Nickname",
        min_length=1,
        description="Nickname cannot be an empty string",
        index=True,
    )
    # TODO: Add field for dateOfBirth
    height: Optional[int] = Field(
        default=None,
        title="Height (in)",
        gt=0,
        description="Height must be positive",
    )
    weight: Optional[int] = Field(
        default=None,
        title="Weight (lbs)",
        gt=0,
        description="Weight must be positive",
    )
    reach: Optional[int] = Field(
        default=None,
        title="Reach (in)",
        gt=0,
        description="Reach must be positive",
    )
    # TODO: Add field for stance
    wins: int = Field(
        default=0,
        nullable=False,
        title="Number of wins",
        ge=0,
        description="Number of wins cannot be negative",
    )
    losses: int = Field(
        default=0,
        nullable=False,
        title="Number of losses",
        ge=0,
        description="Number of losses cannot be negative",
    )
    draws: int = Field(
        default=0,
        nullable=False,
        title="Number of draws",
        ge=0,
        description="Number of draws cannot be negative",
    )
    no_contests: int = Field(
        default=0,
        nullable=False,
        alias="noContests",
        title="Number of no contests",
        ge=0,
        description="Number of no contests cannot be negative",
    )
    current_champion: bool = Field(
        default=False,
        nullable=False,
        alias="currentChampion",
        title="Is the fighter currently a champion?",
    )
    slpm: Optional[float] = Field(
        default=None,
        title="Significant strikes landed per minute",
        ge=0.0,
        description="SLpM cannot be negative",
    )
    str_acc: Optional[float] = Field(
        default=None,
        alias="strAcc",
        title="Significant striking accuracy",
        ge=0.0,
        description="Striking accuracy cannot be negative",
    )
    sapm: Optional[float] = Field(
        default=None,
        title="Significant strikes absorbed per minute",
        ge=0.0,
        description="SApM cannot be negative",
    )
    str_def: Optional[float] = Field(
        default=None,
        alias="strDef",
        title="Significant strike defense",
        ge=0.0,
        description="Strike defense cannot be negative",
    )
    td_avg: Optional[float] = Field(
        default=None,
        alias="tdAvg",
        title="Average takedowns landed per 15 minutes",
        ge=0.0,
        description="TD avg. cannot be negative",
    )
    td_acc: Optional[float] = Field(
        default=None,
        alias="tdAcc",
        title="Takedown accuracy",
        ge=0.0,
        description="Takedown accuracy cannot be negative",
    )
    td_def: Optional[float] = Field(
        default=None,
        alias="tdDef",
        title="Takedown defense",
        ge=0.0,
        description="Takedown defense cannot be negative",
    )
    sub_avg: Optional[float] = Field(
        default=None,
        alias="subAvg",
        title="Average submissions attempted per 15 minutes",
        ge=0.0,
        description="Sub. avg. cannot be negative",
    )
