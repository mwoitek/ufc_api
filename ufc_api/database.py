from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine

from .models.stance import Stance

sqlite_url = "sqlite:///db.sqlite"
connect_args = {"check_same_thread": False}

# TODO: remove echo=True
engine = create_engine(
    sqlite_url,
    echo=True,
    connect_args=connect_args,
)


def create_db() -> None:
    SQLModel.metadata.create_all(engine)


def create_stances() -> None:
    with Session(engine) as session:
        for name in ["Orthodox", "Southpaw", "Switch", "Open Stance", "Sideways"]:
            session.add(Stance(name=name))
        session.commit()
