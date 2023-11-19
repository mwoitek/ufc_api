from fastapi import FastAPI

from .database import create_db
from .database import create_stances

# These imports are here only to guarantee that the SQL
# tables will be created correctly:
from .models.fighter import Fighter  # noqa: F401
from .models.stance import Stance  # noqa: F401

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    create_db()
    create_stances()
