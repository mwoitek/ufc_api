from datetime import date
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from sqlmodel import Session
from sqlmodel import select

from ..database import engine
from ..models.fighter import Fighter
from ..models.fighter import FighterCreate
from ..models.fighter import FighterReadDetailed
from ..models.fighter import FighterReadSimple
from ..models.fighter import FighterUpdate
from ..models.stance import Stance

router = APIRouter(prefix="/fighters", tags=["fighters"])


def convert_date_of_birth(fighter_dict: dict) -> dict:
    date_of_birth = fighter_dict.pop("date_of_birth", None)
    if isinstance(date_of_birth, str):
        fighter_dict["date_of_birth"] = date.fromisoformat(date_of_birth)
    return fighter_dict


def get_stance_id(fighter_dict: dict, session: Session) -> dict:
    stance = fighter_dict.pop("stance", None)
    if isinstance(stance, str):
        statement = select(Stance.id).where(Stance.name == stance)
        stance_id = session.exec(statement).one_or_none()
        if isinstance(stance_id, int):
            fighter_dict["stance_id"] = stance_id
    return fighter_dict


@router.post(
    "/",
    response_model=FighterReadSimple,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_fighter(fighter: FighterCreate) -> FighterReadSimple:
    fighter_dict = fighter.dict()
    fighter_dict = convert_date_of_birth(fighter_dict)

    with Session(engine) as session:
        fighter_dict = get_stance_id(fighter_dict, session)

        db_fighter = Fighter.parse_obj(fighter_dict)
        session.add(db_fighter)
        session.commit()
        session.refresh(db_fighter)

        return FighterReadSimple.from_db_obj(db_fighter)


@router.get("/", response_model=list[FighterReadDetailed], response_model_exclude_none=True)
def read_fighters() -> list[FighterReadDetailed]:
    with Session(engine) as session:
        statement = select(Fighter, Stance).join(Stance, isouter=True)
        results = session.exec(statement)

        response_list = []

        for db_fighter, db_stance in results:
            stance = db_stance.name if db_stance is not None else None
            response_list.append(FighterReadDetailed.from_db_obj(db_fighter, stance))

        return response_list


@router.get("/{fighter_id}", response_model=FighterReadDetailed, response_model_exclude_none=True)
def read_fighter(fighter_id: int) -> FighterReadDetailed:
    with Session(engine) as session:
        fighter = session.get(Fighter, fighter_id)

        if fighter is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found")

        stance: Optional[str] = None
        if isinstance(fighter.stance_id, int):
            db_stance = session.get(Stance, fighter.stance_id)
            if db_stance is not None:
                stance = db_stance.name

        return FighterReadDetailed.from_db_obj(fighter, stance)


@router.patch("/{fighter_id}", response_model=FighterReadSimple, response_model_exclude_none=True)
def update_fighter(fighter_id: int, fighter: FighterUpdate) -> FighterReadSimple:
    with Session(engine) as session:
        db_fighter = session.get(Fighter, fighter_id)

        if db_fighter is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found")

        fighter_dict = fighter.dict(exclude_unset=True)
        fighter_dict = convert_date_of_birth(fighter_dict)
        fighter_dict = get_stance_id(fighter_dict, session)
        fighter_dict["updated_at"] = datetime.now()

        for field, value in fighter_dict.items():
            setattr(db_fighter, field, value)

        session.add(db_fighter)
        session.commit()
        session.refresh(db_fighter)

        return FighterReadSimple.from_db_obj(db_fighter, updated=True)


@router.delete("/{fighter_id}")
def delete_fighter(fighter_id: int) -> dict[str, bool]:
    with Session(engine) as session:
        fighter = session.get(Fighter, fighter_id)

        if fighter is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found")

        session.delete(fighter)
        session.commit()

        return {"ok": True}
