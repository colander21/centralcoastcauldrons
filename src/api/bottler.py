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

#  Fix for multiple potion types
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            connection.execute(sqlalchemy.text(
            f'''UPDATE potions SET num_potions = num_potions + {potion.quantity}
            WHERE percent_red = {potion.potion_type[0]}
            AND percent_green = {potion.potion_type[1]}
            AND percent_blue = {potion.potion_type[2]}
            AND percent_dark = {potion.potion_type[3]};'''))
            connection.execute(sqlalchemy.text(f"UPDATE barrels SET num_ml_red = num_ml_red - {potion.potion_type[0] * potion.quantity}, num_ml_green = num_ml_green - {potion.potion_type[1] * potion.quantity}, num_ml_blue = num_ml_blue - {potion.potion_type[2] * potion.quantity}, num_ml_dark = num_ml_dark - {potion.potion_type[3] * potion.quantity};"))


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
        num_ml_data = connection.execute(sqlalchemy.text(
        '''SELECT potions.id, percent_red, percent_green, percent_blue, percent_dark, num_ml_red, num_ml_green, num_ml_blue, num_ml_dark, name
            FROM barrels
            JOIN potions
                ON potions.percent_red <= barrels.num_ml_red
                AND potions.percent_green <= barrels.num_ml_green
                AND potions.percent_blue <= barrels.num_ml_blue
                AND potions.percent_dark <= barrels.num_ml_dark
            ORDER BY potions.id DESC;''')).fetchall()

    if len(num_ml_data) == 0:
        return bottling_plan
        
    total_ml_red = num_ml_data[0].num_ml_red
    total_ml_green = num_ml_data[0].num_ml_green
    total_ml_blue = num_ml_data[0].num_ml_blue
    total_ml_dark = num_ml_data[0].num_ml_dark
    total_ml = total_ml_red + total_ml_green + total_ml_blue + total_ml_dark

    # 300 and 400 determined by number of distinct potion types in db containing that color of ml multiplied by 100
    # set to 1 for testing data on customers
    max_red_mix = total_ml_red // 300
    max_green_mix = total_ml_green // 300
    max_blue_mix = total_ml_blue // 300
    max_dark_mix = total_ml_dark // 400

    # sets max amount of potions to 10000 so that all ml are mixed when ml inventory is low (ie early game right after shop is burned down)
    if(total_ml <= 500):
        max_red_mix = 10000
        max_green_mix = 10000
        max_blue_mix = 10000
        max_dark_mix = 10000

    for potion_type in num_ml_data:
        if(total_ml_red >= potion_type.percent_red and
            total_ml_green >= potion_type.percent_green and
            total_ml_blue >= potion_type.percent_blue and
            total_ml_dark >= potion_type.percent_dark):

            min_red_mix = 1000000
            min_green_mix = 1000000
            min_blue_mix = 1000000
            min_dark_mix = 1000000

            if potion_type.percent_red > 0:
                min_red_mix = min(total_ml_red // potion_type.percent_red, max_red_mix) 

            if potion_type.percent_green > 0:
                min_green_mix = min(total_ml_green // potion_type.percent_green, max_green_mix)
            
            if potion_type.percent_blue > 0:
                min_blue_mix = min(total_ml_blue // potion_type.percent_blue, max_blue_mix)

            if potion_type.percent_dark > 0:
                min_dark_mix = min(total_ml_dark // potion_type.percent_dark, max_dark_mix)
            
            potions_mixed = min(min_red_mix, min_green_mix, min_blue_mix, min_dark_mix)

            total_ml -= 100
            total_ml_red -= potions_mixed * potion_type.percent_red
            total_ml_green -= potions_mixed * potion_type.percent_green
            total_ml_blue -= potions_mixed * potion_type.percent_blue
            total_ml_dark -= potions_mixed * potion_type.percent_dark
            if potions_mixed > 0:
                bottling_plan.append({
                    "potion_type": [potion_type.percent_red, potion_type.percent_green, potion_type.percent_blue, potion_type.percent_dark],
                    "quantity": potions_mixed
                })


    return bottling_plan

if __name__ == "__main__":
    print(get_bottle_plan())