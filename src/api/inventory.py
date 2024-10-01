from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

class Inventory(BaseModel):
    id: int

    num_green_potions: int
    num_green_ml: int
    gold: int

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        num_potions_cursor = connection.execute(sqlalchemy.text("SELECT num_potions, num_ml, gold, sku FROM global_inventory;"))
        num_potions_data = num_potions_cursor.fetchall()
        
        total_potions = 0
        total_ml = 0
        total_gold = num_potions_data[0].gold

        for entry in num_potions_data:
            print(entry.sku)
            total_potions += entry.num_potions
            total_ml += entry.num_ml

    return {"number_of_potions":total_potions, "ml_in_barrels":total_ml, "gold":total_gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"

