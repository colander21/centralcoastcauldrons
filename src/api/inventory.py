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
        gold_data = connection.execute(sqlalchemy.text("SELECT SUM(gold) AS total_gold FROM global_inventory;")).fetchone()
        potions_data = connection.execute(sqlalchemy.text("SELECT SUM(num_potions) AS total_potions FROM potions;")).fetchone()
        ml_data = connection.execute(sqlalchemy.text("SELECT SUM(num_ml_red + num_ml_green + num_ml_blue + num_ml_dark) AS total_ml from barrels")).fetchone()

    return {"number_of_potions":potions_data.total_potions, "ml_in_barrels":ml_data.total_ml, "gold":gold_data.total_gold}

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

