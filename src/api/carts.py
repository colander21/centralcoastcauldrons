from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import datetime

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    
    with db.engine.begin() as connection:
        result_cursor = connection.execute(sqlalchemy.text(f"SELECT customer_name, character_class, level, cart_id, quantity, total_cost FROM carts WHERE customer_name = '{new_cart.customer_name}' and character_class = '{new_cart.character_class}' and level = '{new_cart.level}';"))
        result_data = result_cursor.fetchall()
        print(result_data)
        print(len(result_data))
        if len(result_data) == 0:
            next_id_cursor = connection.execute(sqlalchemy.text(f"SELECT cart_id FROM carts ORDER BY cart_id DESC;"))
            next_id_data = next_id_cursor.fetchone()
            cart_id = (next_id_data[0]+1)
            print("This is the next cart_id: ",next_id_data.cart_id +1)
            connection.execute(sqlalchemy.text(f"INSERT INTO carts (customer_name, character_class, level, cart_id, quantity, total_cost) VALUES ('{new_cart.customer_name}','{new_cart.character_class}',{new_cart.level},{cart_id},{0},{0});"))
            connection.execute(sqlalchemy.text(f"INSERT INTO shopping_cart (id, quantity_green_potions, quantity_blue_potions, quantity_red_potions) VALUES ('{cart_id}',0,0,0);"))
        else:
            cart_id = result_data[0][3]
            connection.execute(sqlalchemy.text(f"UPDATE carts SET quantity = 0, total_cost = 0 WHERE customer_name = '{new_cart.customer_name}' and character_class = '{new_cart.character_class}' and level = '{new_cart.level}';"))
            connection.execute(sqlalchemy.text(f"UPDATE shopping_cart SET quantity_green_potions = 0, quantity_red_potions = 0, quantity_blue_potions = 0 WHERE id = '{cart_id}';"))
        print("Cart id = ", {cart_id})
    return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int


# TODO create new table in db to track individual cart items with foreign key of cart_id from carts add new entry or update existing entry to all zeros in create_cart()
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):

    print("This is the item sku: ", item_sku)
    """ """
    with db.engine.begin() as connection:
        potion_price_cursor = connection.execute(sqlalchemy.text(f"SELECT price FROM global_inventory WHERE sku = '{item_sku}';"))
        potion_price_data = potion_price_cursor.fetchone()
        connection.execute(sqlalchemy.text(f"UPDATE carts SET quantity = {cart_item.quantity}, total_cost = total_cost + {cart_item.quantity * potion_price_data.price} WHERE cart_id = {cart_id};"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_potions = num_potions - {cart_item.quantity} WHERE sku = '{item_sku}';"))


    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    with db.engine.begin() as connection:
        checkout_cursor = connection.execute(sqlalchemy.text(f"SELECT quantity,total_cost FROM carts WHERE cart_id = {cart_id};"))
        checkout_data = checkout_cursor.fetchone()
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold + {checkout_data.total_cost}"))


    return {"total_potions_bought": checkout_data.quantity, "total_gold_paid": checkout_data.total_cost}
