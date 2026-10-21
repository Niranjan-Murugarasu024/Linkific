-- Indexes speed up selected reads but consume storage and add write overhead.
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_name ON products(product_name);
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date DESC);
CREATE INDEX idx_orders_status_date ON orders(status, order_date DESC);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_status ON payments(payment_status);
CREATE INDEX idx_inventory_product_date ON inventory_movements(product_id, movement_at DESC);

-- Primary keys and UNIQUE constraints already create supporting indexes.
-- Avoid adding duplicate indexes without measuring the workload.
