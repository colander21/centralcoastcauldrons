import sqlalchemy
import database as db

with db.engine.begin() as connection:
    num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory;"))

print(num_green_potions)