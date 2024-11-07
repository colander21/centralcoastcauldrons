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


    if sort_col is search_sort_options.customer_name:
        order_by = db.carts.c.customer_name
    elif sort_col is search_sort_options.item_sku:
        order_by = db.potions.c.id
    elif sort_col is search_sort_options.line_item_total:
        order_by = db.carts.c.total_cost
    elif sort_col is search_sort_options.timestamp:
        order_by = db.carts.c.timestamp
    else:
        assert False

    stmt = (
        sqlalchemy.select(
            db.carts.c.customer_name,
            db.potions.c.name.label('potion_name'),
            db.carts.c.total_cost,
            db.carts.c.timestamp
        ).join(
            db.shopping_cart, db.shopping_cart.c.cart_id == db.carts.c.id
        ).join(
            db.potions, db.potions.c.id == db.shopping_cart.c.potion_id
        )
        .order_by(order_by, db.carts.c.timestamp)
        .offset(5) # for paging offset by page number-1 * 5
        .limit(5)

    )

    # stmt = sqlalchemy.select(db.carts.c.customer_name)

    # filter only if name parameter is passed
    if customer_name != "":
        stmt = stmt.where(db.carts.c.customer_name(f"%{customer_name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "customer": row.customer_name,
                    "item": row.potion_name,
                    "total_cost": row.total_cost,
                    "timestamp": row.timestamp
                }
            )

    return {
        "previous": "",
        "next": "",
        "results": json
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
    print("Current customer: ",  new_cart)
    
    with db.engine.begin() as connection:
        cart_id_data = connection.execute(sqlalchemy.text(f"INSERT INTO carts (customer_name, character_class, level, quantity, total_cost) VALUES ('{new_cart.customer_name}','{new_cart.character_class}',{new_cart.level},0,0) RETURNING id;")).fetchone()

    return {"cart_id": cart_id_data.id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):

    print("This is the item sku: ", item_sku)
    """ """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"INSERT INTO shopping_cart (cart_id, potion_id, quantity) VALUES ({cart_id},{item_sku}, {cart_item.quantity});"))

        potion_price_data = connection.execute(sqlalchemy.text(f"SELECT price FROM potions WHERE id = '{item_sku}';")).fetchone()

        connection.execute(sqlalchemy.text(f"UPDATE carts SET quantity = quantity + {cart_item.quantity}, total_cost = total_cost + {cart_item.quantity * potion_price_data.price} WHERE id = {cart_id};"))

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    with db.engine.begin() as connection:
        # potions_purchased_data = connection.execute(sqlalchemy.text(f"SELECT potion_id, quantity FROM shopping_cart WHERE cart_id = {cart_id};")).fetchall()

        # checkout_data = connection.execute(sqlalchemy.text(f"SELECT quantity AS total_potions,total_cost FROM carts WHERE id = {cart_id};")).fetchone()
        
        # connection.execute(sqlalchemy.text(f"INSERT INTO global_inventory (gold) VALUES ({checkout_data.total_cost});"))

        # for potion in potions_purchased_data:
        #     connection.execute(sqlalchemy.text(f"UPDATE potions SET num_potions = num_potions - {potion.quantity} WHERE id = {potion.potion_id};"))

    
        total_potions = connection.execute(sqlalchemy.text(
            '''INSERT INTO potions_ledger 
            (potion_id, num_potions) 
            VALUES ((SELECT potion_id FROM shopping_cart WHERE cart_id = :cart_id), 
            (SELECT -quantity FROM shopping_cart WHERE cart_id = :cart_id))
            RETURNING num_potions'''),
            {
                "cart_id": cart_id
            }
            ).fetchone()
        
        total_paid = connection.execute(sqlalchemy.text(
            '''INSERT INTO global_inventory 
            (gold) 
            VALUES ((SELECT total_cost FROM carts WHERE id = :cart_id))
            RETURNING gold'''),
            {
                "cart_id": cart_id
            }
            ).fetchone()
            


    return {"total_potions_bought": -total_potions.num_potions, "total_gold_paid": total_paid.gold}
