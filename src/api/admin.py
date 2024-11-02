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
        connection.execute(sqlalchemy.text("DELETE FROM capacity;"))
        connection.execute(sqlalchemy.text("INSERT INTO capacity (potion_capacity, ml_capacity) VALUES (1,1);"))

        connection.execute(sqlalchemy.text("DELETE FROM global_inventory;"))
        connection.execute(sqlalchemy.text("INSERT INTO global_inventory (gold) VALUES (100);"))

        connection.execute(sqlalchemy.text("UPDATE potions SET price = 40;"))

        connection.execute(sqlalchemy.text("DELETE FROM ml_ledger;"))
        connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (ml_id, num_ml) VALUES (1,0);"))
        connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (ml_id, num_ml) VALUES (2,0);"))
        connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (ml_id, num_ml) VALUES (3,0);"))
        connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (ml_id, num_ml) VALUES (4,0);"))

        connection.execute(sqlalchemy.text("DELETE FROM potions_ledger;"))
        for id in range(1,18):
            connection.execute(sqlalchemy.text(f"INSERT INTO potions_ledger (potion_id, num_potions) VALUES ({id},0);"))


    return "OK"

