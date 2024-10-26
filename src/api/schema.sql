CREATE TABLE global_inventory (
    id INT GENERATED ALWAYS AS IDENTITY,
    created_at timestampz DEFAULT now(),
    gold INT,
    PRIMARY KEY(id)
);

CREATE TABLE barrels (
    id INT GENERATED ALWAYS AS IDENTITY,
    created_at timestampz DEFAULT now(),
    num_ml_red INT DEFAULT 0,
    num_ml_green INT DEFAULT 0,
    num_ml_blue INT DEFAULT 0,
    num_ml_dark INT DEFAULT 0,
    PRIMARY KEY(id)
);

CREATE TABLE potions (
    id INT GENERATED ALWAYS AS IDENTITY,
    created_at timestampz DEFAULT now(),
    num_potions INT DEFAULT 0,
    price INT DEFAULT 50,
    percent_red INT DEFAULT 0,
    percent_green INT DEFAULT 0,
    percent_blue INT DEFAULT 0,
    percent_dark INT DEFAULT 0,
    name TEXT,
    PRIMARY KEY(id)
);

CREATE TABLE carts (
    id INT GENERATED ALWAYS AS IDENTITY
    created_at timestampz DEFAULT now(),
    customer_name TEXT,
    character_class TEXT,
    quantity INT DEFAULT 0,
    total_cost DEFAULT 0,
    level INT,
    PRIMARY KEY(id)
);

CREATE TABLE shopping_cart (
    id INT GENERATED ALWAYS AS IDENTITY
    cart_id INT,
    potion_id INT,
    quantity INT DEFAULT 0,

    PRIMARY KEY(id)
    CONSTRAINT fk_carts
      FOREIGN KEY(cart_id)
        REFERENCES carts(id),
    CONSTRAINT fk_potions
      FOREIGN KEY(potion_id)
        REFERENCES potions(id)
)