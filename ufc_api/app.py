from typing import Any

from fastapi import FastAPI
from fastapi import status
from sqlmodel import Session
from sqlmodel import select

from .database import create_db
from .database import create_stances
from .database import engine
from .models.fighter import Fighter
from .models.fighter import FighterCreate
from .models.stance import Stance

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    create_db()
    create_stances()


# TODO: error handling
@app.post("/fighters/", status_code=status.HTTP_201_CREATED)
async def create_fighter(fighter: FighterCreate) -> Any:
    fighter_dict = fighter.dict(by_alias=True)
    stance = fighter_dict.pop("stance", None)

    with Session(engine) as session:
        if isinstance(stance, str):
            statement = select(Stance.id).where(Stance.name == stance)
            stance_id = session.exec(statement).one_or_none()
            if stance_id is not None:
                fighter_dict["stance_id"] = stance_id

        db_fighter = Fighter.parse_obj(fighter_dict)
        session.add(db_fighter)
        session.commit()
        session.refresh(db_fighter)
        return db_fighter
