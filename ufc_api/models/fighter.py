from datetime import date
from datetime import datetime
from typing import Any
from typing import Optional

from pydantic import create_model
from pydantic import root_validator
from sqlmodel import Field
from sqlmodel import SQLModel

# TODO: I HATE this code. There is a lot of repetition. FIND A BETTER SOLUTION!!!!!

field_defs = {
    "first_name": (
        Optional[str],
        Field(default=None, alias="firstName", description="First name", min_length=1, index=True),
    ),
    "last_name": (
        Optional[str],
        Field(default=None, alias="lastName", description="Last name", min_length=1, index=True),
    ),
    "nickname": (
        Optional[str],
        Field(default=None, description="Nickname", min_length=1, index=True),
    ),
    "dob_str": (
        Optional[str],
        Field(default=None, alias="dateOfBirth", description="Date of birth", regex=r"\d{4}-\d{1,2}-\d{1,2}"),
    ),
    "height": (Optional[int], Field(default=None, description="Height (in)", gt=0)),
    "weight": (Optional[int], Field(default=None, description="Weight (lbs)", gt=0)),
    "reach": (Optional[int], Field(default=None, description="Reach (in)", gt=0)),
    "stance": (Optional[str], Field(default=None, description="Stance", min_length=1)),
    "wins": (int, Field(..., description="Number of wins", ge=0, nullable=False)),
    "losses": (int, Field(..., description="Number of losses", ge=0, nullable=False)),
    "draws": (int, Field(..., description="Number of draws", ge=0, nullable=False)),
    "no_contests": (
        int,
        Field(default=0, alias="noContests", description="Number of no contests", ge=0, nullable=False),
    ),
    "current_champion": (
        bool,
        Field(
            default=False,
            alias="currentChampion",
            description="Is the fighter currently a champion?",
            nullable=False,
        ),
    ),
    "slpm": (
        Optional[float],
        Field(default=None, description="Significant strikes landed per minute", ge=0.0),
    ),
    "str_acc": (
        Optional[float],
        Field(default=None, alias="strAcc", description="Significant striking accuracy", ge=0.0),
    ),
    "sapm": (
        Optional[float],
        Field(default=None, description="Significant strikes absorbed per minute", ge=0.0),
    ),
    "str_def": (
        Optional[float],
        Field(default=None, alias="strDef", description="Significant strike defense", ge=0.0),
    ),
    "td_avg": (
        Optional[float],
        Field(default=None, alias="tdAvg", description="Average takedowns landed per 15 minutes", ge=0.0),
    ),
    "td_acc": (Optional[float], Field(default=None, alias="tdAcc", description="Takedown accuracy", ge=0.0)),
    "td_def": (Optional[float], Field(default=None, alias="tdDef", description="Takedown defense", ge=0.0)),
    "sub_avg": (
        Optional[float],
        Field(
            default=None,
            alias="subAvg",
            description="Average submissions attempted per 15 minutes",
            ge=0.0,
        ),
    ),
}


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


FighterCreate = create_model(
    "FighterCreate",
    __base__=SQLModel,
    __validators__={"full_name_validator": root_validator()(check_full_name)},
    **field_defs,
)


class Fighter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    first_name: Optional[str] = Field(alias="firstName", index=True)
    last_name: Optional[str] = Field(alias="lastName", index=True)
    nickname: Optional[str] = Field(index=True)

    date_of_birth: Optional[date] = Field(default=None, alias="dateOfBirth")

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


class FighterNames(SQLModel):
    first_name: Optional[str] = Field(alias="firstName", description="First name")
    last_name: Optional[str] = Field(alias="lastName", description="Last name")
    nickname: Optional[str] = Field(description="Nickname")

    # FIXME: Add correct type
    @classmethod
    def from_db_obj(cls, db_obj: Any) -> "FighterNames":
        data_dict = {}
        for k, v in cls.__fields__.items():
            field = v.alias if isinstance(v.alias, str) else k
            data_dict[field] = getattr(db_obj, k)
        return cls.parse_obj(data_dict)


class FighterPhysicalFeatures(SQLModel):
    height: Optional[int] = Field(description="Height (in)")
    weight: Optional[int] = Field(description="Weight (lbs)")
    reach: Optional[int] = Field(description="Reach (in)")

    # FIXME: Add correct type
    @classmethod
    def from_db_obj(cls, db_obj: Any) -> Optional["FighterPhysicalFeatures"]:
        data_dict = {k: getattr(db_obj, k) for k in cls.__fields__}
        return cls.parse_obj(data_dict) if any(v is not None for v in data_dict.values()) else None


class FighterRecord(SQLModel):
    wins: int = Field(description="Number of wins")
    losses: int = Field(description="Number of losses")
    draws: int = Field(description="Number of draws")
    no_contests: int = Field(alias="noContests", description="Number of no contests")

    # FIXME: Add correct type
    @classmethod
    def from_db_obj(cls, db_obj: Any) -> "FighterRecord":
        data_dict = {}
        for k, v in cls.__fields__.items():
            field = v.alias if isinstance(v.alias, str) else k
            data_dict[field] = getattr(db_obj, k)
        return cls.parse_obj(data_dict)


class FighterCareerStats(SQLModel):
    slpm: float = Field(description="Significant strikes landed per minute")
    str_acc: float = Field(alias="strAcc", description="Significant striking accuracy")
    sapm: float = Field(description="Significant strikes absorbed per minute")
    str_def: float = Field(alias="strDef", description="Significant strike defense")
    td_avg: float = Field(alias="tdAvg", description="Average takedowns landed per 15 minutes")
    td_acc: float = Field(alias="tdAcc", description="Takedown accuracy")
    td_def: float = Field(alias="tdDef", description="Takedown defense")
    sub_avg: float = Field(alias="subAvg", description="Average submissions attempted per 15 minutes")

    # FIXME: Add correct type
    @classmethod
    def from_db_obj(cls, db_obj: Any) -> Optional["FighterCareerStats"]:
        data_dict = {}
        for k, v in cls.__fields__.items():
            field = v.alias if isinstance(v.alias, str) else k
            data_dict[field] = getattr(db_obj, k)
        return cls.parse_obj(data_dict) if all(isinstance(s, float) for s in data_dict.values()) else None


class FighterReadDetailed(SQLModel):
    names: FighterNames = Field(description="All known names")
    date_of_birth: Optional[str] = Field(alias="dateOfBirth", description="Date of birth")
    physical_features: Optional[FighterPhysicalFeatures] = Field(
        alias="physicalFeatures",
        description="Physical features",
    )
    stance: Optional[str] = Field(description="Stance")
    record: FighterRecord = Field(description="MMA record")
    current_champion: bool = Field(
        alias="currentChampion",
        description="Is the fighter currently a champion?",
    )
    career_stats: Optional[FighterCareerStats] = Field(alias="careerStats", description="Career statistics")

    # FIXME: Add correct type
    @classmethod
    def from_db_obj(cls, db_obj: Any) -> "FighterReadDetailed":
        data_dict = {
            "names": FighterNames.from_db_obj(db_obj),
            "dateOfBirth": str(db_obj.date_of_birth) if isinstance(db_obj.date_of_birth, date) else None,
            "physicalFeatures": FighterPhysicalFeatures.from_db_obj(db_obj),
            "stance": db_obj.stance,
            "record": FighterRecord.from_db_obj(db_obj),
            "currentChampion": db_obj.current_champion,
            "careerStats": FighterCareerStats.from_db_obj(db_obj),
        }
        return cls.parse_obj(data_dict)
