from fastapi import FastAPI

from .database import create_db
from .database import create_stances
from .models.fighter import Fighter  # noqa: F401
from .models.stance import Stance  # noqa: F401
from .routers import fighters

app = FastAPI()
app.include_router(fighters.router)


@app.on_event("startup")
def on_startup() -> None:
    create_db()
    create_stances()
