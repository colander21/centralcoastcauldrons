from fastapi import APIRouter

import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        catalog_list = []
        """catalog_cursor = connection.execute(sqlalchemy.text("SELECT sku,name,num_potions,price  FROM global_inventory WHERE sku = 'GREEN_POTION_0';"))
        catalog_data = catalog_cursor.fetchall()

        new_catalog_item = {}

        #TODO: make dynamic
        for item in catalog_data:
            if item.num_potions > 0:
                new_catalog_item = {"sku": item.sku, "name": item.name, "quantity": item.num_potions, "price": item.price, }"""
        
        green_potion_cursor = connection.execute(sqlalchemy.text("SELECT sku,name,num_potions,price  FROM global_inventory WHERE sku = 'GREEN_POTION_0';"))
        green_potion_data = green_potion_cursor.fetchone()

        blue_potion_cursor = connection.execute(sqlalchemy.text("SELECT sku,name,num_potions,price  FROM global_inventory WHERE sku = 'BLUE_POTION_0';"))
        blue_potion_data = blue_potion_cursor.fetchone()

        red_potion_cursor = connection.execute(sqlalchemy.text("SELECT sku,name,num_potions,price  FROM global_inventory WHERE sku = 'RED_POTION_0';"))
        red_potion_data = red_potion_cursor.fetchone()



    if green_potion_data.num_potions > 0:
        catalog_list.append({
                "sku": green_potion_data.sku,
                "name": green_potion_data.name,
                "quantity": green_potion_data.num_potions,
                "price": green_potion_data.price,
                "potion_type": [0, 100, 0, 0],
            })
    
    if blue_potion_data.num_potions > 0:
        catalog_list.append({
                "sku": blue_potion_data.sku,
                "name": blue_potion_data.name,
                "quantity": blue_potion_data.num_potions,
                "price": blue_potion_data.price,
                "potion_type": [0, 0, 100, 0],
            })
        
    if red_potion_data.num_potions > 0:
        catalog_list.append({
            "sku": red_potion_data.sku,
            "name": red_potion_data.name,
            "quantity": red_potion_data.num_potions,
            "price": red_potion_data.price,
            "potion_type": [100, 0, 0, 0],
        })
    

    return catalog_list