from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("DELETE FROM global_inventory;"))
        connection.execute(sqlalchemy.text("INSERT INTO global_inventory (gold) VALUES (100);"))
        connection.execute(sqlalchemy.text("UPDATE barrels SET num_ml_red = 0, num_ml_green = 0, num_ml_dark = 0, num_ml_blue = 0;"))
        connection.execute(sqlalchemy.text("UPDATE potions SET num_potions = 0, price = 50;"))


    
    return "OK"

