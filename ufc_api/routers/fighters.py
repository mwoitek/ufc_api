from datetime import date

from fastapi import APIRouter
from fastapi import status
from sqlmodel import Session
from sqlmodel import select

from ..database import engine
from ..models.fighter import Fighter
from ..models.fighter import FighterCreate
from ..models.fighter import FighterReadSimple
from ..models.stance import Stance

router = APIRouter(prefix="/fighters/", tags=["fighters"])


# TODO: Implement error handling
@router.post("/", response_model=FighterReadSimple, status_code=status.HTTP_201_CREATED)
def create_fighter(fighter: FighterCreate) -> FighterReadSimple:
    fighter_dict = fighter.dict(by_alias=True)

    # If necessary, add date of birth
    date_of_birth = fighter_dict.pop("dateOfBirth", None)
    if isinstance(date_of_birth, str):
        fighter_dict["dateOfBirth"] = date.fromisoformat(date_of_birth)

    with Session(engine) as session:
        # If stance was passed, get the corresponding ID
        stance = fighter_dict.pop("stance", None)
        if isinstance(stance, str):
            statement = select(Stance.id).where(Stance.name == stance.title())
            stance_id = session.exec(statement).one_or_none()
            if stance_id is not None:
                fighter_dict["stance_id"] = stance_id

        # Add fighter to DB, and refresh its data
        db_fighter = Fighter.parse_obj(fighter_dict)
        session.add(db_fighter)
        session.commit()
        session.refresh(db_fighter)

        return FighterReadSimple.from_db_obj(db_fighter)
