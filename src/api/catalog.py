from fastapi import APIRouter

import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    catalog_list = []
    
    with db.engine.begin() as connection:
        """catalog_cursor = connection.execute(sqlalchemy.text("SELECT sku,name,num_potions,price  FROM global_inventory WHERE sku = 'GREEN_POTION_0';"))
        catalog_data = catalog_cursor.fetchall()

        new_catalog_item = {}

        #TODO: make dynamic
        for item in catalog_data:
            if item.num_potions > 0:
                new_catalog_item = {"sku": item.sku, "name": item.name, "quantity": item.num_potions, "price": item.price, }"""
        
        '''green_potion_cursor = connection.execute(sqlalchemy.text("SELECT sku,name,num_potions,price  FROM global_inventory WHERE sku = 'GREEN_POTION_0';"))
        green_potion_data = green_potion_cursor.fetchone()

        blue_potion_cursor = connection.execute(sqlalchemy.text("SELECT sku,name,num_potions,price  FROM global_inventory WHERE sku = 'BLUE_POTION_0';"))
        blue_potion_data = blue_potion_cursor.fetchone()

        red_potion_cursor = connection.execute(sqlalchemy.text("SELECT sku,name,num_potions,price  FROM global_inventory WHERE sku = 'RED_POTION_0';"))
        red_potion_data = red_potion_cursor.fetchone()'''

        potions_data = connection.execute(sqlalchemy.text("SELECT id, num_ml, num_potions, price, percent_red, percent_green, percent_blue, percent_dark, name FROM potions;")).fetchall()
       
    count_of_skus = 0

    for potion in potions_data:
        print(potion)
        if count_of_skus == 6:
            break
        if potion.num_potions > 0:
            count_of_skus += 1
            catalog_list.append({
                "sku": potion.id,
                "name": potion.name,
                "quantity": potion.num_potions,
                "price": potion.price,
                "potion_type": [potion.percent_red, potion.percent_green, potion.percent_blue, potion.percent_dark],
            })
    
    return catalog_list