# Database design notes

## Entities and relationships
- `customers` 1-to-many `orders`
- `categories` 1-to-many `products`
- `orders` 1-to-many `order_items`
- `products` 1-to-many `order_items`
- `orders` 1-to-many `payments`
- `products` 1-to-many `inventory_movements`

`order_items` resolves the many-to-many relationship between orders and products. It stores the purchase-time unit price so historical order values do not change when a product's current price changes.

## Integrity
- Primary keys uniquely identify rows.
- Foreign keys prevent orphaned references.
- `NOT NULL`, `UNIQUE`, and `CHECK` constraints enforce local business rules.
- `NUMERIC(12,2)` is used for monetary values rather than floating-point types.
- `ON DELETE RESTRICT` protects referenced customers/products. Order items cascade when an order is deleted, but production systems often retain orders for audit and accounting reasons.

## Indexes
Indexes are added to common join and filter columns. Indexes improve some reads but use disk and increase insert/update/delete cost. Validate choices with realistic query plans.

## Deliberate simplifications
This is a learning schema, not a production commerce platform. It does not implement tax, shipping charges, discounts, refunds as separate ledger entries, multi-warehouse inventory, currency conversion, or row-level security. Payment amounts are sample values and are not guaranteed to reconcile with order totals.
