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
        
        total_ml_red = num_ml_data[0].num_ml_red
        total_ml_green = num_ml_data[0].num_ml_green
        total_ml_blue = num_ml_data[0].num_ml_blue
        total_ml_dark = num_ml_data[0].num_ml_dark

    for potion_type in num_ml_data:
        if(potion_type.num_ml_red >= potion_type.percent_red and
            potion_type.num_ml_green >= potion_type.percent_green and
            potion_type.num_ml_blue >= potion_type.percent_blue and
            potion_type.num_ml_dark >= potion_type.percent_dark):

            total_ml_red -= potion_type.percent_red
            total_ml_green -= potion_type.percent_green
            total_ml_blue -= potion_type.percent_blue
            total_ml_dark -= potion_type.percent_dark
            bottling_plan.append({
                "potion_type": [potion_type.percent_red, potion_type.percent_green, potion_type.percent_blue, potion_type.percent_dark],
                "quantity": 1,
            })
            print(f"{potion_type.name} potion added to bottling plan")


    return bottling_plan

if __name__ == "__main__":
    print(get_bottle_plan())