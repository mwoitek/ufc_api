from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class Stance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(nullable=False)
