from datetime import date
from datetime import datetime
from typing import Any
from typing import Optional

from pydantic import root_validator
from pydantic import validator
from sqlmodel import Field
from sqlmodel import SQLModel

VALID_STANCES = {"Orthodox", "Southpaw", "Switch", "Open Stance", "Sideways"}
DESC = {
    "id": "ID",
    "created_at": "Date and time of creation",
    "updated_at": "Date and time of update",
    "first_name": "First name",
    "last_name": "Last name",
    "nickname": "Nickname",
    "names": "All known names",
    "date_of_birth": "Date of birth",
    "height": "Height (in)",
    "weight": "Weight (lbs)",
    "reach": "Reach (in)",
    "physical_features": "Physical features",
    "stance": "Stance",
    "wins": "Number of wins",
    "losses": "Number of losses",
    "draws": "Number of draws",
    "no_contests": "Number of no contests",
    "record": "MMA record",
    "current_champion": "Is the fighter currently a champion?",
    "slpm": "Significant strikes landed per minute",
    "str_acc": "Significant striking accuracy",
    "sapm": "Significant strikes absorbed per minute",
    "str_def": "Significant strike defense",
    "td_avg": "Average takedowns landed per 15 minutes",
    "td_acc": "Takedown accuracy",
    "td_def": "Takedown defense",
    "sub_avg": "Average submissions attempted per 15 minutes",
    "career_stats": "Career statistics",
}


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
    first_name: Optional[str] = Field(default=None, description=DESC["first_name"])
    last_name: Optional[str] = Field(default=None, description=DESC["last_name"])
    nickname: Optional[str] = Field(default=None, description=DESC["nickname"])
    date_of_birth: Optional[str] = Field(
        default=None,
        description=DESC["date_of_birth"],
        regex=r"\d{4}-\d{1,2}-\d{1,2}",
    )
    height: Optional[int] = Field(default=None, description=DESC["height"], gt=0)
    weight: Optional[int] = Field(default=None, description=DESC["weight"], gt=0)
    reach: Optional[int] = Field(default=None, description=DESC["reach"], gt=0)
    stance: Optional[str] = Field(default=None, description=DESC["stance"])
    wins: int = Field(default=0, description=DESC["wins"], ge=0)
    losses: int = Field(default=0, description=DESC["losses"], ge=0)
    draws: int = Field(default=0, description=DESC["draws"], ge=0)
    no_contests: int = Field(default=0, description=DESC["no_contests"], ge=0)
    current_champion: bool = Field(default=False, description=DESC["current_champion"])
    slpm: Optional[float] = Field(default=None, description=DESC["slpm"], ge=0.0)
    str_acc: Optional[float] = Field(default=None, description=DESC["str_acc"], ge=0.0)
    sapm: Optional[float] = Field(default=None, description=DESC["sapm"], ge=0.0)
    str_def: Optional[float] = Field(default=None, description=DESC["str_def"], ge=0.0)
    td_avg: Optional[float] = Field(default=None, description=DESC["td_avg"], ge=0.0)
    td_acc: Optional[float] = Field(default=None, description=DESC["td_acc"], ge=0.0)
    td_def: Optional[float] = Field(default=None, description=DESC["td_def"], ge=0.0)
    sub_avg: Optional[float] = Field(default=None, description=DESC["sub_avg"], ge=0.0)

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
    first_name: Optional[str] = Field(description=DESC["first_name"])
    last_name: Optional[str] = Field(description=DESC["last_name"])
    nickname: Optional[str] = Field(description=DESC["nickname"])


class FighterReadSimple(CustomSQLModel):
    id: int = Field(..., description=DESC["id"])
    created_at: Optional[datetime] = Field(default=None, description=DESC["created_at"])
    updated_at: Optional[datetime] = Field(default=None, description=DESC["updated_at"])
    names: Names = Field(..., description=DESC["names"])

    @classmethod
    def from_db_obj(cls, db_obj: Fighter, updated: bool = False) -> "FighterReadSimple":
        dt_field = "updated_at" if updated else "created_at"
        data = db_obj.dict(include={"id", dt_field, "first_name", "last_name", "nickname"})
        names = Names(
            first_name=data.pop("first_name"),
            last_name=data.pop("last_name"),
            nickname=data.pop("nickname"),
        )
        return cls(names=names, **data)


class PhysicalFeatures(SQLModel):
    height: Optional[int] = Field(description=DESC["height"])
    weight: Optional[int] = Field(description=DESC["weight"])
    reach: Optional[int] = Field(description=DESC["reach"])


class Record(CustomSQLModel):
    wins: int = Field(..., description=DESC["wins"])
    losses: int = Field(..., description=DESC["losses"])
    draws: int = Field(..., description=DESC["draws"])
    no_contests: int = Field(..., description=DESC["no_contests"])


class CareerStats(CustomSQLModel):
    slpm: Optional[float] = Field(description=DESC["slpm"])
    str_acc: Optional[float] = Field(description=DESC["str_acc"])
    sapm: Optional[float] = Field(description=DESC["sapm"])
    str_def: Optional[float] = Field(description=DESC["str_def"])
    td_avg: Optional[float] = Field(description=DESC["td_avg"])
    td_acc: Optional[float] = Field(description=DESC["td_acc"])
    td_def: Optional[float] = Field(description=DESC["td_def"])
    sub_avg: Optional[float] = Field(description=DESC["sub_avg"])


class FighterReadDetailed(CustomSQLModel):
    id: int = Field(..., description=DESC["id"])
    names: Names = Field(..., description=DESC["names"])
    date_of_birth: Optional[date] = Field(description=DESC["date_of_birth"])
    physical_features: Optional[PhysicalFeatures] = Field(description=DESC["physical_features"])
    stance: Optional[str] = Field(description=DESC["stance"])
    record: Record = Field(..., description=DESC["record"])
    current_champion: bool = Field(..., description=DESC["current_champion"])
    career_stats: Optional[CareerStats] = Field(description=DESC["career_stats"])

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
    first_name: Optional[str] = Field(default=None, description=DESC["first_name"])
    last_name: Optional[str] = Field(default=None, description=DESC["last_name"])
    nickname: Optional[str] = Field(default=None, description=DESC["nickname"])
    date_of_birth: Optional[str] = Field(
        default=None,
        description=DESC["date_of_birth"],
        regex=r"\d{4}-\d{1,2}-\d{1,2}",
    )
    height: Optional[int] = Field(default=None, description=DESC["height"], gt=0)
    weight: Optional[int] = Field(default=None, description=DESC["weight"], gt=0)
    reach: Optional[int] = Field(default=None, description=DESC["reach"], gt=0)
    stance: Optional[str] = Field(default=None, description=DESC["stance"])
    wins: Optional[int] = Field(default=None, description=DESC["wins"], ge=0)
    losses: Optional[int] = Field(default=None, description=DESC["losses"], ge=0)
    draws: Optional[int] = Field(default=None, description=DESC["draws"], ge=0)
    no_contests: Optional[int] = Field(default=None, description=DESC["no_contests"], ge=0)
    current_champion: Optional[bool] = Field(default=None, description=DESC["current_champion"])
    slpm: Optional[float] = Field(default=None, description=DESC["slpm"], ge=0.0)
    str_acc: Optional[float] = Field(default=None, description=DESC["str_acc"], ge=0.0)
    sapm: Optional[float] = Field(default=None, description=DESC["sapm"], ge=0.0)
    str_def: Optional[float] = Field(default=None, description=DESC["str_def"], ge=0.0)
    td_avg: Optional[float] = Field(default=None, description=DESC["td_avg"], ge=0.0)
    td_acc: Optional[float] = Field(default=None, description=DESC["td_acc"], ge=0.0)
    td_def: Optional[float] = Field(default=None, description=DESC["td_def"], ge=0.0)
    sub_avg: Optional[float] = Field(default=None, description=DESC["sub_avg"], ge=0.0)

    _check_stance = validator("stance", allow_reuse=True)(check_stance)

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1
