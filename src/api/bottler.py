from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    num_green_potions_mixed = 0
    num_red_potions_mixed = 0
    num_blue_potions_mixed = 0

    for item in potions_delivered:
        if item.potion_type[1] == 100:
            num_green_potions_mixed += item.quantity
        if item.potion_type[0] == 100:
            num_red_potions_mixed += item.quantity
        if item.potion_type[2] == 100:
            num_blue_potions_mixed += item.quantity
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_potions = num_potions + {num_green_potions_mixed} WHERE sku = 'GREEN_POTION_0';"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = num_ml - {num_green_potions_mixed*100} WHERE sku = 'GREEN_POTION_0';"))

        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_potions = num_potions + {num_red_potions_mixed} WHERE sku = 'RED_POTION_0';"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = num_ml - {num_red_potions_mixed*100} WHERE sku = 'RED_POTION_0';"))
        
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_potions = num_potions + {num_blue_potions_mixed} WHERE sku = 'BLUE_POTION_0';"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = num_ml - {num_blue_potions_mixed*100} WHERE sku = 'BLUE_POTION_0';"))

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    bottling_plan = []

    with db.engine.begin() as connection:
        num_ml_cursor = connection.execute(sqlalchemy.text("SELECT sku,num_ml,num_potions FROM global_inventory;"))
        num_ml_data = num_ml_cursor.fetchall()

    for entry in num_ml_data:
        if entry.sku == "GREEN_POTION_0":
            num_green_ml = entry.num_ml
        if entry.sku == "BLUE_POTION_0":
            num_blue_ml = entry.num_ml
        if entry.sku == "RED_POTION_0":
            num_red_ml = entry.num_ml

    
    num_green_potions_mixed = num_green_ml // 100
    num_red_potions_mixed = num_red_ml // 100
    num_blue_potions_mixed = num_blue_ml //100

    while(num_blue_potions_mixed+num_red_potions_mixed+num_green_potions_mixed+num_ml_data[0].num_potions > 50):
        num_blue_potions_mixed -= 1
        num_green_potions_mixed -= 1
        num_red_potions_mixed -= 1

    
    if num_green_potions_mixed > 0:
        bottling_plan.append({
             "potion_type": [0, 100, 0, 0],
            "quantity": num_green_potions_mixed,
        })
    if num_red_potions_mixed > 0:
        bottling_plan.append({
            "potion_type": [100, 0, 0, 0],
            "quantity": num_red_potions_mixed,
        })
    if num_blue_potions_mixed > 0:
        bottling_plan.append({
            "potion_type": [0, 0, 100, 0],
            "quantity": num_blue_potions_mixed,
        })


    return bottling_plan

if __name__ == "__main__":
    print(get_bottle_plan())