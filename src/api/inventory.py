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
        potions_data = connection.execute(sqlalchemy.text("SELECT SUM(num_potions) AS total_potions FROM potions_ledger;")).fetchone()
        ml_data = connection.execute(sqlalchemy.text("SELECT SUM(num_ml) AS total_ml from ml_ledger")).fetchone()

    return {"number_of_potions":potions_data.total_potions, "ml_in_barrels":ml_data.total_ml, "gold":gold_data.total_gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    inventory = get_inventory()
    total_gold = inventory["gold"]
    print(inventory)
    potion_cap_plan = 0
    ml_cap_plan = 0

    with db.engine.begin() as connection:
        capacity_data = connection.execute(sqlalchemy.text("SELECT SUM(potion_capacity) AS potion_capacity, SUM(ml_capacity) AS ml_capacity FROM capacity;")).fetchone()

    if(inventory["number_of_potions"] > (0.50 * capacity_data.potion_capacity * 50) and total_gold > 1000):
        potion_cap_plan += 1
        total_gold -= 1000

    if(inventory["ml_in_barrels"] > (0.50 * capacity_data.ml_capacity * 10000) and total_gold > 1000):
        ml_cap_plan += 1
        total_gold -= 1000

    return {
        "potion_capacity": potion_cap_plan,
        "ml_capacity": ml_cap_plan
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

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            '''INSERT INTO capacity 
            (potion_capacity, ml_capacity) 
            VALUES (:potion_cap, :ml_cap)'''),
            {
                "potion_cap": capacity_purchase.potion_capacity,
                "ml_cap": capacity_purchase.ml_capacity
            }
            )

    return "OK"

