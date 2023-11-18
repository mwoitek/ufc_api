from sqlmodel import SQLModel
from sqlmodel import create_engine

sqlite_url = f"sqlite:///db.sqlite"
connect_args = {"check_same_thread": False}

# TODO: remove echo=True
engine = create_engine(
    sqlite_url,
    echo=True,
    connect_args=connect_args,
)


def create_db() -> None:
    SQLModel.metadata.create_all(engine)
