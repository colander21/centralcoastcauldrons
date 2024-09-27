from fastapi import APIRouter

import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        num_green_potions_cursor = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory;"))
        num_green_potions_data = num_green_potions_cursor.fetchone()

    if num_green_potions_data[0] == 0:
        return []

    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": num_green_potions_data[0],
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            }
        ]