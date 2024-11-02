from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/info",
    tags=["info"],
    dependencies=[Depends(auth.get_api_key)],
)

class Timestamp(BaseModel):
    day: str
    hour: int

@router.post("/current_time")
def post_time(timestamp: Timestamp):
    """
    Share current time.
    """

    print("This is the current day", timestamp.day)

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            '''UPDATE day 
            SET current_day = :current_day'''),
            {
                "current_day": timestamp.day
            }
            )

    return "OK"

