from datetime import date
from datetime import datetime
from typing import Any
from typing import Optional

from pydantic import create_model
from pydantic import root_validator
from pydantic import validator
from sqlmodel import Field
from sqlmodel import SQLModel

FIELDS = {
    "id_required": (int, Field(..., alias="id", description="ID")),
    "created_at": (
        datetime,
        Field(
            default_factory=datetime.now,
            alias="createdAt",
            description="Date and time of creation",
            nullable=False,
        ),
    ),
    "updated_at": (
        datetime,
        Field(
            default_factory=datetime.now,
            alias="updatedAt",
            description="Date and time of update",
            nullable=False,
        ),
    ),
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


def get_full_name(values: dict) -> str:
    first_name = values.get("first_name")
    if not isinstance(first_name, str):
        first_name = ""

    last_name = values.get("last_name")
    if not isinstance(last_name, str):
        last_name = ""

    return (first_name + " " + last_name).strip()


def check_full_name(cls, values: dict) -> dict:
    if get_full_name(values) == "":
        raise ValueError("fighter has no name")
    return values


fields = {k: v for k, v in FIELDS.items() if k not in ["id_required", "created_at", "updated_at"]}
FighterCreate = create_model(
    "FighterCreate",
    __base__=SQLModel,
    __validators__={"full_name_validator": root_validator()(check_full_name)},
    **fields,
)

fields = {
    "id": (Optional[int], Field(default=None, primary_key=True, nullable=False)),
    "date_of_birth": (Optional[date], Field(default=None)),
    "stance_id": (Optional[int], Field(default=None, foreign_key="stance.id")),
}
fields.update(FIELDS)
field_keys = [
    "id",
    "created_at",
    "updated_at",
    "first_name",
    "last_name",
    "nickname",
    "date_of_birth",
    "height",
    "weight",
    "reach",
    "stance_id",
    "wins",
    "losses",
    "draws",
    "no_contests",
    "current_champion",
    "slpm",
    "str_acc",
    "sapm",
    "str_def",
    "td_avg",
    "td_acc",
    "td_def",
    "sub_avg",
]
fields = {k: fields[k] for k in field_keys}
Fighter = create_model("Fighter", __base__=SQLModel, __cls_kwargs__={"table": True}, **fields)


def fill_full_name(cls, value: Optional[str], values: dict) -> str:
    if value is not None:
        return value
    return get_full_name(values)


fields = {k: FIELDS[k] for k in ["id_required", "created_at", "updated_at", "first_name", "last_name"]}
fields["first_name"][1].exclude = True
fields["last_name"][1].exclude = True
fields.update(full_name=(Optional[str], Field(default=None, alias="fullName", description="Full name")))
FighterReadSimple = create_model(
    "FighterReadSimple",
    __base__=SQLModel,
    __validators__={"full_name_filler": validator("full_name", always=True)(fill_full_name)},
    **fields,
)

fields = {k: FIELDS[k] for k in ["first_name", "last_name", "nickname"]}
Names = create_model("Names", __base__=SQLModel, **fields)

fields = {k: FIELDS[k] for k in ["height", "weight", "reach"]}
PhysicalFeatures = create_model("PhysicalFeatures", __base__=SQLModel, **fields)

fields = {k: FIELDS[k] for k in ["wins", "losses", "draws", "no_contests"]}
Record = create_model("Record", __base__=SQLModel, **fields)

field_keys = ["slpm", "str_acc", "sapm", "str_def", "td_avg", "td_acc", "td_def", "sub_avg"]
fields = {k: FIELDS[k] for k in field_keys}
CareerStats = create_model("CareerStats", __base__=SQLModel, **fields)

fields = {k: FIELDS[k] for k in ["id_required", "stance", "current_champion"]}
fields.update(
    names=(Names, Field(..., description="All known names")),
    date_of_birth=(Optional[date], Field(default=None, alias="dateOfBirth", description="Date of birth")),
    physical_features=(
        Optional[PhysicalFeatures],
        Field(default=None, alias="physicalFeatures", description="Physical features"),
    ),
    record=(Record, Field(..., description="MMA record")),
    career_stats=(
        Optional[CareerStats],
        Field(default=None, alias="careerStats", description="Career statistics"),
    ),
)
field_keys = [
    "id_required",
    "names",
    "date_of_birth",
    "physical_features",
    "stance",
    "record",
    "current_champion",
    "career_stats",
]
fields = {k: fields[k] for k in field_keys}
FighterReadDetailed = create_model("FighterReadDetailed", __base__=SQLModel, **fields)


# FIXME
def from_db_obj(cls, db_obj: Any) -> FighterReadDetailed:
    data_dict = {
        "id": db_obj.id,
        "names": Names(first_name=db_obj.first_name, last_name=db_obj.last_name, nickname=db_obj.nickname),
        "dateOfBirth": db_obj.date_of_birth,
        "physicalFeatures": PhysicalFeatures(height=db_obj.height, weight=db_obj.weight, reach=db_obj.reach),
        "stance": db_obj.stance,
        "record": Record(
            wins=db_obj.wins,
            losses=db_obj.losses,
            draws=db_obj.draws,
            no_contests=db_obj.no_contests,
        ),
        "currentChampion": db_obj.current_champion,
        "careerStats": CareerStats(
            slpm=db_obj.slpm,
            str_acc=db_obj.str_acc,
            sapm=db_obj.sapm,
            str_def=db_obj.str_def,
            td_avg=db_obj.td_avg,
            td_acc=db_obj.td_acc,
            td_def=db_obj.td_def,
            sub_avg=db_obj.sub_avg,
        ),
    }
    return cls.parse_obj(data_dict)


FighterReadDetailed.from_db_obj = classmethod(from_db_obj)
