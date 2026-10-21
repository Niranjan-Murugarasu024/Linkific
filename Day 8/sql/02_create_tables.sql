-- Execute while connected to ecommerce_practice.
CREATE TABLE customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(30),
    city VARCHAR(100),
    state VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT customers_email_not_blank CHECK (length(trim(email)) > 0)
);

CREATE TABLE categories (
    category_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id BIGINT NOT NULL REFERENCES categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    product_name VARCHAR(200) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    order_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','paid','processing','shipped','delivered','cancelled','refunded')),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(100),
    notes TEXT
);

CREATE TABLE order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    CONSTRAINT order_items_order_product_unique UNIQUE (order_id, product_id)
);

CREATE TABLE payments (
    payment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    payment_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    payment_method VARCHAR(30) NOT NULL
        CHECK (payment_method IN ('card','upi','net_banking','wallet','cash_on_delivery')),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (payment_status IN ('pending','successful','failed','refunded')),
    transaction_reference VARCHAR(100) UNIQUE
);

CREATE TABLE inventory_movements (
    movement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity_change INTEGER NOT NULL CHECK (quantity_change <> 0),
    reason VARCHAR(30) NOT NULL
        CHECK (reason IN ('restock','sale','return','adjustment')),
    movement_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
