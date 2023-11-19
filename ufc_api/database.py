from pathlib import Path

from sqlalchemy import func
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import select

from .models.stance import Stance

sqlite_file_name = "db.sqlite"

engine = create_engine(
    f"sqlite:///{sqlite_file_name}",
    connect_args={"check_same_thread": False},
    echo=True,  # TODO: remove
)


def create_db() -> None:
    # If DB already exists, do nothing
    sqlite_file_path = Path(__file__).resolve().parents[1] / sqlite_file_name
    if sqlite_file_path.exists() and sqlite_file_path.is_file():
        return
    SQLModel.metadata.create_all(engine)


def create_stances() -> None:
    with Session(engine) as session:
        # If table is not empty, do nothing
        statement = select(func.count(Stance.id))
        count = session.exec(statement).one()
        if count > 0:
            return

        # Populate table
        for name in ["Orthodox", "Southpaw", "Switch", "Open Stance", "Sideways"]:
            session.add(Stance(name=name))
        session.commit()
