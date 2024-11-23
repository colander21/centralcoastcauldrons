from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import random

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
        #connection.execute(sqlalchemy.text(f"UPDATE barrels SET num_ml_red = num_ml_red + {num_red_ml_delivered}, num_ml_green = num_ml_green + {num_green_ml_delivered}, num_ml_blue = num_ml_blue + {num_blue_ml_delivered}, num_ml_dark = num_ml_dark + {num_dark_ml_delivered}"))
        if num_red_ml_delivered > 0:
            connection.execute(sqlalchemy.text(
                '''INSERT INTO ml_ledger 
                (ml_id, num_ml) 
                VALUES (:color, :num_ml)'''),
                {
                    "color": 1,
                    "num_ml": num_red_ml_delivered
                })
        if num_green_ml_delivered > 0:
            connection.execute(sqlalchemy.text(
                '''INSERT INTO ml_ledger 
                (ml_id, num_ml) 
                VALUES (:color, :num_ml)'''),
                {
                    "color": 2,
                    "num_ml": num_green_ml_delivered
                })
        if num_blue_ml_delivered > 0:
            connection.execute(sqlalchemy.text(
                '''INSERT INTO ml_ledger 
                (ml_id, num_ml) 
                VALUES (:color, :num_ml)'''),
                {
                    "color": 3,
                    "num_ml": num_blue_ml_delivered
                })
        if num_dark_ml_delivered > 0:
            connection.execute(sqlalchemy.text(
                '''INSERT INTO ml_ledger 
                (ml_id, num_ml) 
                VALUES (:color, :num_ml)'''),
                {
                    "color": 4,
                    "num_ml": num_dark_ml_delivered
                })

        connection.execute(sqlalchemy.text(f"INSERT INTO global_inventory (gold) VALUES (:gold);"), [{"gold": -total_cost}])

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(f"\nPre shuffle {wholesale_catalog}\n")

    random.shuffle(wholesale_catalog)

    print(f"\nPost Shuffle {wholesale_catalog}")

    purchase_plan = []

    with db.engine.begin() as connection:
        ml_data = connection.execute(sqlalchemy.text("SELECT SUM(num_ml) AS total_ml FROM ml_ledger;")).fetchone()
        gold_data = connection.execute(sqlalchemy.text("SELECT SUM(gold) AS total_gold FROM global_inventory;")).fetchone()
        capacity_data = connection.execute(sqlalchemy.text("SELECT SUM(potion_capacity) AS potion_capacity, SUM(ml_capacity) AS ml_capacity FROM capacity;")).fetchone()


    num_small_green_barrels_to_purchase = 0
    num_small_red_barrels_to_purchase = 0
    num_small_blue_barrels_to_purchase = 0
    num_medium_blue_barrels_to_purchase = 0
    num_medium_green_barrels_to_purchase = 0
    num_medium_red_barrels_to_purchase = 0
    num_large_blue_barrels_to_purchase = 0
    num_large_green_barrels_to_purchase = 0
    num_large_red_barrels_to_purchase = 0

    num_large_dark_barrels_to_purchase = 0
    total_ml = ml_data.total_ml
    total_gold = gold_data.total_gold

    # Decide what size barrels to buy
    barrel_allowances = allowance(total_gold, capacity_data.ml_capacity)
    print("Barrel Allowance: ", barrel_allowances)
    #barrel_allowances["barrel_size"] = "medium"

    count_red_barrels_bought = 0
    count_green_barrels_bought = 0
    count_blue_barrels_bought = 0
    count_dark_barrels_bought = 0

    if barrel_allowances.get("barrel_size") == "small":
        for item in wholesale_catalog:
            if ((total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)) and item.price <= total_gold:
                if item.sku == "SMALL_GREEN_BARREL":
                    while(item.price <= total_gold and item.quantity > 0 and count_green_barrels_bought < 5 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_small_green_barrels_to_purchase +=1
                        total_gold -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought small green barrel")
                        count_green_barrels_bought += 1
                elif item.sku == "SMALL_BLUE_BARREL":
                    while(item.price <= total_gold and item.quantity > 0 and count_blue_barrels_bought < 5 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_small_blue_barrels_to_purchase +=1
                        total_gold -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought small blue barrel")
                        count_blue_barrels_bought += 1
                elif item.sku == "SMALL_RED_BARREL":
                    while(item.price <= total_gold and item.quantity > 0 and count_red_barrels_bought < 5 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_small_red_barrels_to_purchase +=1
                        total_gold -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought small red barrel")
                        count_red_barrels_bought += 1
    

    if barrel_allowances["barrel_size"] == "medium":
        for item in wholesale_catalog:
            if ((total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)) and item.price <= total_gold:
                if item.sku == "MEDIUM_GREEN_BARREL":
                    while(item.price <= barrel_allowances["green_barrel_allowance"] and item.quantity > 0 and count_green_barrels_bought < 5 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_medium_green_barrels_to_purchase +=1
                        barrel_allowances["green_barrel_allowance"] -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought medium green barrel")
                        count_green_barrels_bought += 1
                elif item.sku == "MEDIUM_BLUE_BARREL":
                    while(item.price <= barrel_allowances["blue_barrel_allowance"] and item.quantity > 0 and count_blue_barrels_bought < 5 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_medium_blue_barrels_to_purchase +=1
                        barrel_allowances["blue_barrel_allowance"] -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought medium blue barrel")
                        count_blue_barrels_bought += 1
                elif item.sku == "MEDIUM_RED_BARREL":
                    while(item.price <= barrel_allowances["red_barrel_allowance"] and item.quantity > 0 and count_red_barrels_bought < 5 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_medium_red_barrels_to_purchase +=1
                        barrel_allowances["red_barrel_allowance"] -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought medium red barrel")
                        count_red_barrels_bought += 1

    if barrel_allowances["barrel_size"] == "large":
        for item in wholesale_catalog:
            print("current item: ", item)
            if ((total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)) and item.price <= total_gold:
                print("able to buy this item")
                if item.sku == "LARGE_GREEN_BARREL":
                    print("This is large green")
                    while(item.price <= barrel_allowances["green_barrel_allowance"] and item.quantity > 0 and count_green_barrels_bought < 1 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_large_green_barrels_to_purchase +=1
                        barrel_allowances["green_barrel_allowance"] -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought large green barrel")
                        count_green_barrels_bought += 1
                elif item.sku == "LARGE_BLUE_BARREL":
                    print("This is large blue")
                    while(item.price <= barrel_allowances["blue_barrel_allowance"] and item.quantity > 0 and count_blue_barrels_bought < 1 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_large_blue_barrels_to_purchase +=1
                        barrel_allowances["blue_barrel_allowance"] -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought large blue barrel")
                        count_blue_barrels_bought += 1
                elif item.sku == "LARGE_RED_BARREL":
                    print("This is large red")
                    while(item.price <= barrel_allowances["red_barrel_allowance"] and item.quantity > 0 and count_red_barrels_bought < 1 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_large_red_barrels_to_purchase +=1
                        barrel_allowances["red_barrel_allowance"] -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought large red barrel")
                        count_red_barrels_bought += 1
                elif item.sku == "LARGE_DARK_BARREL":
                    print("This is large dark")
                    while(item.price <= barrel_allowances["dark_barrel_allowance"] and item.quantity > 0 and count_dark_barrels_bought < 1 and (total_ml + item.ml_per_barrel) <= (capacity_data.ml_capacity * 10000)):
                        num_large_dark_barrels_to_purchase +=1
                        barrel_allowances["dark_barrel_allowance"] -= item.price
                        total_ml += item.ml_per_barrel
                        print("Bought large dark barrel")
                        count_dark_barrels_bought += 1



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

    if(num_large_green_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "LARGE_GREEN_BARREL",
            "quantity": num_large_green_barrels_to_purchase,
        })
    if(num_large_red_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "LARGE_RED_BARREL",
            "quantity": num_large_red_barrels_to_purchase,
        })
    if(num_large_blue_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "LARGE_BLUE_BARREL",
            "quantity": num_large_blue_barrels_to_purchase,
        })
    if(num_large_dark_barrels_to_purchase > 0):
        purchase_plan.append({
            "sku": "SMALL_DARK_BARREL",
            "quantity": num_large_dark_barrels_to_purchase,
        })


    return purchase_plan



def allowance(total_gold, ml_capacity):
    allowance_plan = {}
    if total_gold >= 2000 and ml_capacity >= 4:
        allowance_plan = {"red_barrel_allowance": total_gold//4,
                        "green_barrel_allowance": total_gold//4,
                        "blue_barrel_allowance": total_gold//4,
                        "dark_barrel_allowance": total_gold//4,
                        "barrel_size": "large"}
    elif total_gold >= 750 and ml_capacity >= 2:
        allowance_plan = {"red_barrel_allowance": total_gold//3,
                        "green_barrel_allowance": total_gold//3,
                        "blue_barrel_allowance": total_gold//3,
                        "dark_barrel_allowance": 0,
                        "barrel_size": "medium"}
    else:
        allowance_plan = {"red_barrel_allowance": total_gold,
                        "green_barrel_allowance": total_gold,
                        "blue_barrel_allowance": total_gold,
                        "dark_barrel_allowance": 0,
                        "barrel_size": "small"}
    return allowance_plan
    
    