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

        potions_data = connection.execute(sqlalchemy.text(
            '''SELECT SUM(potions_ledger.num_potions) AS num_potions, potions.id, price, percent_red, percent_green, percent_blue, percent_dark, name 
            FROM potions 
            JOIN potions_ledger
                ON potions_ledger.potion_id = potions.id
            GROUP BY potions.id
            HAVING SUM(potions_ledger.num_potions) > 0
            ORDER BY num_potions DESC,
                SUM(potions_ledger.num_potions)''')).fetchall()

        count_skus = 0
        
    
    if len(potions_data) > 0:  
        for potion in potions_data:
            if count_skus == 6:
                break
            print(potion)
            catalog_list.append({
                "sku": potion.id,
                "name": potion.name,
                "quantity": potion.num_potions,
                "price": potion.price,
                "potion_type": [potion.percent_red, potion.percent_green, potion.percent_blue, potion.percent_dark]
            })
            count_skus += 1
    
    return catalog_list