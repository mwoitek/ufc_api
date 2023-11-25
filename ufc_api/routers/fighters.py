from datetime import date

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


# TODO: Implement error handling
@router.post(
    "/",
    response_model=FighterReadSimple,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_fighter(fighter: FighterCreate) -> FighterReadSimple:
    fighter_dict = fighter.dict()

    # If necessary, add date of birth
    date_of_birth = fighter_dict.pop("date_of_birth")
    if isinstance(date_of_birth, str):
        fighter_dict["date_of_birth"] = date.fromisoformat(date_of_birth)

    with Session(engine) as session:
        # If stance was passed, get the corresponding ID
        stance = fighter_dict.pop("stance")
        if isinstance(stance, str):
            statement = select(Stance.id).where(Stance.name == stance)
            stance_id = session.exec(statement).one_or_none()
            if stance_id is not None:
                fighter_dict["stance_id"] = stance_id

        # Add fighter to DB, and refresh its data
        db_fighter = Fighter.parse_obj(fighter_dict)
        session.add(db_fighter)
        session.commit()
        session.refresh(db_fighter)

        return FighterReadSimple.from_db_obj(db_fighter)


@router.get("/{fighter_id}", response_model=FighterReadDetailed, response_model_exclude_none=True)
def read_fighter(fighter_id: int) -> FighterReadDetailed:
    with Session(engine) as session:
        fighter = session.get(Fighter, fighter_id)

        if fighter is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found")

        # If necessary, get stance from the corresponding ID
        stance_id = fighter.stance_id
        stance = session.get(Stance, stance_id).name if isinstance(stance_id, int) else None

        return FighterReadDetailed.from_db_obj(fighter, stance)


@router.patch("/{fighter_id}", response_model=FighterReadSimple, response_model_exclude_none=True)
def update_fighter(fighter_id: int, fighter: FighterUpdate) -> FighterReadSimple:
    with Session(engine) as session:
        db_fighter = session.get(Fighter, fighter_id)

        if db_fighter is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found")

        fighter_dict = fighter.dict(exclude_unset=True)

        date_of_birth = fighter_dict.pop("date_of_birth", None)
        if isinstance(date_of_birth, str):
            fighter_dict["date_of_birth"] = date.fromisoformat(date_of_birth)

        stance = fighter_dict.pop("stance", None)
        if isinstance(stance, str):
            statement = select(Stance.id).where(Stance.name == stance)
            stance_id = session.exec(statement).one_or_none()
            if stance_id is not None:
                fighter_dict["stance_id"] = stance_id

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
