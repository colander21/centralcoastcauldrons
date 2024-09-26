from fastapi import APIRouter

import sqlalchemy
from src import database as db
from .inventory import get_inventory

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    inventory = get_inventory()
    num_green_potions = inventory["num_green_potions"]


    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": num_green_potions,
                "price": 75,
                "potion_type": [0, 100, 0, 0],
            }
        ]
