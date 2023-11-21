from fastapi import FastAPI
from fastapi import status
from sqlmodel import Session
from sqlmodel import select

from .database import create_db
from .database import create_stances
from .database import engine
from .models.fighter import Fighter
from .models.fighter import FighterCreate
from .models.fighter import FighterReadSimple
from .models.stance import Stance

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    create_db()
    create_stances()


# TODO: error handling
@app.post("/fighters/", response_model=FighterReadSimple, status_code=status.HTTP_201_CREATED)
def create_fighter(fighter: FighterCreate) -> FighterReadSimple:
    fighter_dict = fighter.dict(by_alias=True)
    stance = fighter_dict.pop("stance", None)

    with Session(engine) as session:
        # If stance was passed, get the corresponding ID
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
