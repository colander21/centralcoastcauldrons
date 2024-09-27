from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    num_green_ml_delivered = 0
    total_cost = 0

    for barrel in barrels_delivered:
        if barrel.sku == "SMALL_GREEN_BARREL":
            num_green_ml_delivered += barrel.quantity * barrel.ml_per_barrel
            total_cost += barrel.price * barrel.quantity


    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = num_green_ml + {num_green_ml_delivered};"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_cost};"))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory;"))
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory;"))

    num_small_green_barrels_to_purchase = 0

    for item in wholesale_catalog:
        if item.sku == "SMALL_GREEN_BARREL" and num_green_potions < 10 and item.price <= gold:
            num_small_green_barrels_to_purchase +=1
            gold -= item.price


    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": num_small_green_barrels_to_purchase,
        }
    ]

