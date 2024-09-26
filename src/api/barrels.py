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

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    
    num_green_barrels_to_purchase = 0


    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("select num_green_potions from global_inventory;"))
        num_green_potions = result

    if num_green_potions < 10:
        num_green_barrels_to_purchase +=1


    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": num_green_barrels_to_purchase,
        }
    ]

