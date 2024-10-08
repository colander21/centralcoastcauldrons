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
    num_blue_ml_delivered = 0
    num_red_ml_delivered = 0
    total_cost = 0

    for barrel in barrels_delivered:
        if barrel.potion_type[1] == 1:
            num_green_ml_delivered += barrel.quantity * barrel.ml_per_barrel
            print("Green ml: ", num_green_ml_delivered)
            total_cost += barrel.price * barrel.quantity
        if barrel.potion_type[2] == 1:
            num_blue_ml_delivered += barrel.quantity * barrel.ml_per_barrel
            total_cost += barrel.price * barrel.quantity
            print("Blue ml: ", num_blue_ml_delivered)
        if barrel.potion_type[0] == 1:
            num_red_ml_delivered += barrel.quantity * barrel.ml_per_barrel
            total_cost += barrel.price * barrel.quantity
            print("Red ml: ", num_red_ml_delivered)


    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = num_ml + {num_green_ml_delivered} WHERE sku = 'GREEN_POTION_0';"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = num_ml + {num_red_ml_delivered} WHERE sku = 'RED_POTION_0';"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_ml = num_ml + {num_blue_ml_delivered} WHERE sku = 'BLUE_POTION_0';"))

        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_cost};"))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    purchase_plan = []

    with db.engine.begin() as connection:
        inventory_cursor = connection.execute(sqlalchemy.text("SELECT sku,num_potions, gold FROM global_inventory;"))
        inventory_data = inventory_cursor.fetchall()

    total_gold = inventory_data[0].gold
    total_green_potions = 0
    total_red_potions = 0
    total_blue_potions = 0
    for entry in inventory_data:
        if entry.sku == "GREEN_POTION_0":
            total_green_potions = entry.num_potions
        if entry.sku == "RED_POTION_0":
            total_red_potions = entry.num_potions
        if entry.sku == "BLUE_POTION_0":
            total_blue_potions = entry.num_potions

    print("Num green : ", total_green_potions)
    print("Num blue : ", total_blue_potions)
    print("Num red : ", total_red_potions)

    num_small_green_barrels_to_purchase = 0
    num_small_red_barrels_to_purchase = 0
    num_small_blue_barrels_to_purchase = 0

    num_medium_blue_barrels_to_purchase = 0
    num_medium_green_barrels_to_purchase = 0
    num_medium_red_barrels_to_purchase = 0

    for item in wholesale_catalog:
        if total_green_potions <= 10 and item.price <= total_gold:
            if item.sku == "SMALL_GREEN_BARREL":
                num_small_green_barrels_to_purchase +=1
                total_gold -= item.price
                print("Bought small green barrel")
            elif item.sku == "MEDIUM_GREEN_BARREL" and total_green_potions + total_blue_potions + total_red_potions <= 10:
                num_medium_green_barrels_to_purchase +=1
                total_gold -= item.price
                print("Bought medium green barrel")
        if total_blue_potions <= 10 and item.price <= total_gold:
            if item.sku == "SMALL_BLUE_BARREL":
                num_small_blue_barrels_to_purchase +=1
                total_gold -= item.price
                print("Bought small blue barrel")
            '''elif item.sku == "MEDIUM_BLUE_BARREL":
                num_medium_blue_barrels_to_purchase +=1
                total_gold -= item.price
                print("Bought medium blue barrel")'''
        if total_red_potions <= 10 and item.price <= total_gold:
            if item.sku == "SMALL_RED_BARREL":
                num_small_red_barrels_to_purchase +=1
                total_gold -= item.price
                print("Bought small red barrel")
            '''elif item.sku == "MEDIUM_RED_BARREL":
                num_medium_red_barrels_to_purchase +=1
                total_gold -= item.price
                print("Bought medium red barrel")'''


    if(num_small_green_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "SMALL_GREEN_BARREL",
            "quantity": num_small_green_barrels_to_purchase,
        })
    if(num_small_red_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "SMALL_RED_BARREL",
            "quantity": num_small_red_barrels_to_purchase,
        })
    if(num_small_blue_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "SMALL_BLUE_BARREL",
            "quantity": num_small_blue_barrels_to_purchase,
        })

    if(num_medium_green_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "MEDIUM_GREEN_BARREL",
            "quantity": num_medium_green_barrels_to_purchase,
        })
    if(num_medium_red_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "MEDIUM_RED_BARREL",
            "quantity": num_medium_red_barrels_to_purchase,
        })
    if(num_medium_blue_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "MEDIUM_BLUE_BARREL",
            "quantity": num_medium_blue_barrels_to_purchase,
        })

    return purchase_plan
