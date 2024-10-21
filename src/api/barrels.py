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
    num_dark_ml_delivered = 0
    total_cost = 0

    for barrel in barrels_delivered:
        if barrel.potion_type[0] == 1:
            num_red_ml_delivered += barrel.quantity * barrel.ml_per_barrel
            total_cost += barrel.price * barrel.quantity
            print("Red ml: ", num_red_ml_delivered)
        elif barrel.potion_type[1] == 1:
            num_green_ml_delivered += barrel.quantity * barrel.ml_per_barrel
            print("Green ml: ", num_green_ml_delivered)
            total_cost += barrel.price * barrel.quantity
        elif barrel.potion_type[2] == 1:
            num_blue_ml_delivered += barrel.quantity * barrel.ml_per_barrel
            total_cost += barrel.price * barrel.quantity
            print("Blue ml: ", num_blue_ml_delivered)
        elif barrel.potion_type[3] == 1:
            num_dark_ml_delivered += barrel.quantity * barrel.ml_per_barrel
            total_cost += barrel.price * barrel.quantity
            print("Red ml: ", num_dark_ml_delivered)


    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE barrels SET num_ml_red = num_ml_red + {num_red_ml_delivered}, num_ml_green = num_ml_green + {num_green_ml_delivered}, num_ml_blue = num_ml_blue + {num_blue_ml_delivered}, num_ml_dark = num_ml_dark + {num_dark_ml_delivered}"))

        connection.execute(sqlalchemy.text(f"INSERT INTO global_inventory (gold) VALUES (:gold);"), [{"gold": -total_cost}])

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    purchase_plan = []

    with db.engine.begin() as connection:
        potions_data = connection.execute(sqlalchemy.text("SELECT SUM(num_potions) AS total_potions FROM potions;")).fetchone()
        ml_data = connection.execute(sqlalchemy.text("SELECT SUM(num_ml_red + num_ml_green + num_ml_blue + num_ml_dark) AS total_ml FROM barrels;")).fetchone()
        gold_data = connection.execute(sqlalchemy.text("SELECT SUM(gold) AS total_gold FROM global_inventory;")).fetchone()
        #capacity_data = connection.execute(sqlalchemy.text("SELECT SUM(potion_capacity) AS potion_capacity, SUM(ml_capacity) AS ml_capacity FROM capacity;")).fetchone()


    num_small_green_barrels_to_purchase = 0
    num_small_red_barrels_to_purchase = 0
    num_small_blue_barrels_to_purchase = 0
    num_small_dark_barrels_to_purchase = 0
    num_mini_dark_barrels_to_purchase = 0
    total_ml = ml_data.total_ml
    total_gold = gold_data.total_gold

    # num_medium_blue_barrels_to_purchase = 0
    # num_medium_green_barrels_to_purchase = 0
    # num_medium_red_barrels_to_purchase = 0
    # num_medium_dark_barrels_to_purchase = 0


# For later - make categories to choose what size barrels to buy depending on total_gold
    for item in wholesale_catalog:
        # still need to fix based on potion cap * something
        if potions_data.total_potions < 15 and total_ml <= 10000 and item.price <= total_gold:
            if item.sku == "SMALL_GREEN_BARREL":
                num_small_green_barrels_to_purchase +=1
                total_gold -= item.price
                total_ml += item.ml_per_barrel
                print("Bought small green barrel")
            elif item.sku == "SMALL_BLUE_BARREL":
                num_small_blue_barrels_to_purchase +=1
                total_gold -= item.price
                total_ml += item.ml_per_barrel
                print("Bought small blue barrel")
            elif item.sku == "SMALL_RED_BARREL":
                num_small_red_barrels_to_purchase +=1
                total_gold -= item.price
                total_ml += item.ml_per_barrel
                print("Bought small red barrel")
            elif item.sku == "SMALL_DARK_BARREL": #Do small dark barrels exist or is it just mini?
                num_small_dark_barrels_to_purchase +=1
                total_gold -= item.price
                total_ml += item.ml_per_barrel
                print("Bought small dark barrel")
            elif item.sku == "MINI_DARK_BARREL":
                num_mini_dark_barrels_to_purchase +=1
                total_gold -= item.price
                total_ml += item.ml_per_barrel
                print("Bought mini dark barrel")





        # if total_green_potions <= 10 and item.price <= total_gold:
        #     if item.sku == "SMALL_GREEN_BARREL":
        #       num_small_green_barrels_to_purchase +=1
        #       total_gold -= item.price
        #       print("Bought small green barrel")
        #     elif item.sku == "MEDIUM_GREEN_BARREL" and total_green_potions + total_blue_potions + total_red_potions <= 10:
        #         num_medium_green_barrels_to_purchase +=1
        #         total_gold -= item.price
        #         print("Bought medium green barrel")
        # if total_blue_potions <= 10 and item.price <= total_gold:
        #     if item.sku == "SMALL_BLUE_BARREL":
        #         num_small_blue_barrels_to_purchase +=1
        #         total_gold -= item.price
        #         print("Bought small blue barrel")
        #     '''elif item.sku == "MEDIUM_BLUE_BARREL":
        #         num_medium_blue_barrels_to_purchase +=1
        #         total_gold -= item.price
        #         print("Bought medium blue barrel")'''
        # if total_red_potions <= 10 and item.price <= total_gold:
        #     if item.sku == "SMALL_RED_BARREL":
        #         num_small_red_barrels_to_purchase +=1
        #         total_gold -= item.price
        #         print("Bought small red barrel")
        #     '''elif item.sku == "MEDIUM_RED_BARREL":
        #         num_medium_red_barrels_to_purchase +=1
        #         total_gold -= item.price
        #         print("Bought medium red barrel")'''
        


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
    if(num_small_dark_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "SMALL_DARK_BARREL",
            "quantity": num_small_dark_barrels_to_purchase,
        })
    if(num_mini_dark_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "MINI_DARK_BARREL",
            "quantity": num_mini_dark_barrels_to_purchase,
        })

    # if(num_medium_green_barrels_to_purchase > 0):
    #     purchase_plan.append({
    #         "sku": "MEDIUM_GREEN_BARREL",
    #         "quantity": num_medium_green_barrels_to_purchase,
    #     })
    # if(num_medium_red_barrels_to_purchase > 0):
    #     purchase_plan.append({
    #         "sku": "MEDIUM_RED_BARREL",
    #         "quantity": num_medium_red_barrels_to_purchase,
    #     })
    # if(num_medium_blue_barrels_to_purchase > 0):
    #     purchase_plan.append({
    #         "sku": "MEDIUM_BLUE_BARREL",
    #         "quantity": num_medium_blue_barrels_to_purchase,
    #     })

    return purchase_plan
