from typing import Generator, Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session
from app.core.RedBook import RedBook
from app.core.SSE import SSEManager
from app.core.AI import AI
from app.models import *

# DB depends
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=False)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# AI depends
AIDep = Annotated[AI, Depends(AI)]


# SSE depends
def get_sse_manager() -> SSEManager:
    return SSEManager()


SSEDep = Annotated[SSEManager, Depends(get_sse_manager)]


# RedBook depends
def get_redBook_manager() -> RedBook:
    return RedBook()


RedBookDep = Annotated[RedBook, Depends(get_redBook_manager)]
