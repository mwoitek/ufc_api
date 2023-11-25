from datetime import date
from datetime import datetime
from typing import Any
from typing import Optional

from pydantic import root_validator
from pydantic import validator
from sqlmodel import Field
from sqlmodel import SQLModel

VALID_STANCES = {"Orthodox", "Southpaw", "Switch", "Open Stance", "Sideways"}


def to_camel_case(s: str) -> str:
    parts = s.split("_")
    return parts[0] if len(parts) == 1 else parts[0] + "".join(p.capitalize() for p in parts[1:])


class CustomSQLModel(SQLModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True


def check_stance(stance: Optional[str]) -> Optional[str]:
    if stance is None:
        return
    stance = stance.title()
    if stance not in VALID_STANCES:
        raise ValueError("invalid stance")
    return stance


class FighterCreate(CustomSQLModel):
    first_name: Optional[str] = Field(default=None, description="First name")
    last_name: Optional[str] = Field(default=None, description="Last name")
    nickname: Optional[str] = Field(default=None, description="Nickname")
    date_of_birth: Optional[str] = Field(
        default=None,
        description="Date of birth",
        regex=r"\d{4}-\d{1,2}-\d{1,2}",
    )
    height: Optional[int] = Field(default=None, description="Height (in)", gt=0)
    weight: Optional[int] = Field(default=None, description="Weight (lbs)", gt=0)
    reach: Optional[int] = Field(default=None, description="Reach (in)", gt=0)
    stance: Optional[str] = Field(default=None, description="Stance")
    wins: int = Field(default=0, description="Number of wins", ge=0)
    losses: int = Field(default=0, description="Number of losses", ge=0)
    draws: int = Field(default=0, description="Number of draws", ge=0)
    no_contests: int = Field(default=0, description="Number of no contests", ge=0)
    current_champion: bool = Field(default=False, description="Is the fighter currently a champion?")
    slpm: Optional[float] = Field(default=None, description="Significant strikes landed per minute", ge=0.0)
    str_acc: Optional[float] = Field(default=None, description="Significant striking accuracy", ge=0.0)
    sapm: Optional[float] = Field(default=None, description="Significant strikes absorbed per minute", ge=0.0)
    str_def: Optional[float] = Field(default=None, description="Significant strike defense", ge=0.0)
    td_avg: Optional[float] = Field(
        default=None,
        description="Average takedowns landed per 15 minutes",
        ge=0.0,
    )
    td_acc: Optional[float] = Field(default=None, description="Takedown accuracy", ge=0.0)
    td_def: Optional[float] = Field(default=None, description="Takedown defense", ge=0.0)
    sub_avg: Optional[float] = Field(
        default=None,
        description="Average submissions attempted per 15 minutes",
        ge=0.0,
    )

    _check_stance = validator("stance", allow_reuse=True)(check_stance)

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1

    @root_validator
    def check_full_name(cls, values: dict) -> dict:
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
    first_name: Optional[str] = Field(index=True)
    last_name: Optional[str] = Field(index=True)
    nickname: Optional[str] = Field(index=True)
    date_of_birth: Optional[date] = Field(default=None)
    height: Optional[int]
    weight: Optional[int]
    reach: Optional[int]
    stance_id: Optional[int] = Field(default=None, foreign_key="stance.id")
    wins: int = Field(nullable=False)
    losses: int = Field(nullable=False)
    draws: int = Field(nullable=False)
    no_contests: int = Field(nullable=False)
    current_champion: bool = Field(nullable=False)
    slpm: Optional[float]
    str_acc: Optional[float]
    sapm: Optional[float]
    str_def: Optional[float]
    td_avg: Optional[float]
    td_acc: Optional[float]
    td_def: Optional[float]
    sub_avg: Optional[float]


class Names(CustomSQLModel):
    first_name: Optional[str] = Field(description="First name")
    last_name: Optional[str] = Field(description="Last name")
    nickname: Optional[str] = Field(description="Nickname")


class FighterReadSimple(CustomSQLModel):
    id: int = Field(..., description="ID")
    created_at: Optional[datetime] = Field(default=None, description="Date and time of creation")
    updated_at: Optional[datetime] = Field(default=None, description="Date and time of update")
    names: Names = Field(..., description="All known names")

    @classmethod
    def from_db_obj(cls, db_obj: Fighter, updated: bool = False) -> "FighterReadSimple":
        dt_field = "updated_at" if updated else "created_at"
        response_data = db_obj.dict(include={"id", dt_field, "first_name", "last_name", "nickname"})
        names = Names(
            first_name=response_data.pop("first_name"),
            last_name=response_data.pop("last_name"),
            nickname=response_data.pop("nickname"),
        )
        return cls(names=names, **response_data)


class PhysicalFeatures(SQLModel):
    height: Optional[int] = Field(description="Height (in)")
    weight: Optional[int] = Field(description="Weight (lbs)")
    reach: Optional[int] = Field(description="Reach (in)")


class Record(CustomSQLModel):
    wins: int = Field(..., description="Number of wins")
    losses: int = Field(..., description="Number of losses")
    draws: int = Field(..., description="Number of draws")
    no_contests: int = Field(..., description="Number of no contests")


class CareerStats(CustomSQLModel):
    slpm: Optional[float] = Field(description="Significant strikes landed per minute")
    str_acc: Optional[float] = Field(description="Significant striking accuracy")
    sapm: Optional[float] = Field(description="Significant strikes absorbed per minute")
    str_def: Optional[float] = Field(description="Significant strike defense")
    td_avg: Optional[float] = Field(description="Average takedowns landed per 15 minutes")
    td_acc: Optional[float] = Field(description="Takedown accuracy")
    td_def: Optional[float] = Field(description="Takedown defense")
    sub_avg: Optional[float] = Field(description="Average submissions attempted per 15 minutes")


class FighterReadDetailed(CustomSQLModel):
    id: int = Field(..., description="ID")
    names: Names = Field(..., description="All known names")
    date_of_birth: Optional[date] = Field(description="Date of birth")
    physical_features: Optional[PhysicalFeatures] = Field(description="Physical features")
    stance: Optional[str] = Field(description="Stance")
    record: Record = Field(..., description="MMA record")
    current_champion: bool = Field(..., description="Is the fighter currently a champion?")
    career_stats: Optional[CareerStats] = Field(description="Career statistics")

    # FIXME: Add specific type
    @classmethod
    def from_db_obj(cls, db_obj: Any, stance: Optional[str] = None) -> "FighterReadDetailed":
        return cls(
            id=db_obj.id,
            names=Names(first_name=db_obj.first_name, last_name=db_obj.last_name, nickname=db_obj.nickname),
            date_of_birth=db_obj.date_of_birth,
            physical_features=PhysicalFeatures(
                height=db_obj.height,
                weight=db_obj.weight,
                reach=db_obj.reach,
            ),
            stance=db_obj.stance if hasattr(db_obj, "stance") else stance,
            record=Record(
                wins=db_obj.wins,
                losses=db_obj.losses,
                draws=db_obj.draws,
                no_contests=db_obj.no_contests,
            ),
            current_champion=db_obj.current_champion,
            career_stats=CareerStats(
                slpm=db_obj.slpm,
                str_acc=db_obj.str_acc,
                sapm=db_obj.sapm,
                str_def=db_obj.str_def,
                td_avg=db_obj.td_avg,
                td_acc=db_obj.td_acc,
                td_def=db_obj.td_def,
                sub_avg=db_obj.sub_avg,
            ),
        )

    @validator("physical_features")
    def check_physical_features(
        cls,
        physical_features: Optional[PhysicalFeatures],
    ) -> Optional[PhysicalFeatures]:
        if physical_features is None:
            return
        return physical_features if any(v is not None for v in physical_features.dict().values()) else None

    @validator("career_stats")
    def check_career_stats(cls, career_stats: Optional[CareerStats]) -> Optional[CareerStats]:
        if career_stats is None:
            return
        return career_stats if all(isinstance(v, float) for v in career_stats.dict().values()) else None


class FighterUpdate(CustomSQLModel):
    first_name: Optional[str] = Field(default=None, description="First name")
    last_name: Optional[str] = Field(default=None, description="Last name")
    nickname: Optional[str] = Field(default=None, description="Nickname")
    date_of_birth: Optional[str] = Field(
        default=None,
        description="Date of birth",
        regex=r"\d{4}-\d{1,2}-\d{1,2}",
    )
    height: Optional[int] = Field(default=None, description="Height (in)", gt=0)
    weight: Optional[int] = Field(default=None, description="Weight (lbs)", gt=0)
    reach: Optional[int] = Field(default=None, description="Reach (in)", gt=0)
    stance: Optional[str] = Field(default=None, description="Stance")
    wins: Optional[int] = Field(default=None, description="Number of wins", ge=0)
    losses: Optional[int] = Field(default=None, description="Number of losses", ge=0)
    draws: Optional[int] = Field(default=None, description="Number of draws", ge=0)
    no_contests: Optional[int] = Field(default=None, description="Number of no contests", ge=0)
    current_champion: Optional[bool] = Field(default=None, description="Is the fighter currently a champion?")
    slpm: Optional[float] = Field(default=None, description="Significant strikes landed per minute", ge=0.0)
    str_acc: Optional[float] = Field(default=None, description="Significant striking accuracy", ge=0.0)
    sapm: Optional[float] = Field(default=None, description="Significant strikes absorbed per minute", ge=0.0)
    str_def: Optional[float] = Field(default=None, description="Significant strike defense", ge=0.0)
    td_avg: Optional[float] = Field(
        default=None,
        description="Average takedowns landed per 15 minutes",
        ge=0.0,
    )
    td_acc: Optional[float] = Field(default=None, description="Takedown accuracy", ge=0.0)
    td_def: Optional[float] = Field(default=None, description="Takedown defense", ge=0.0)
    sub_avg: Optional[float] = Field(
        default=None,
        description="Average submissions attempted per 15 minutes",
        ge=0.0,
    )

    _check_stance = validator("stance", allow_reuse=True)(check_stance)

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1
