-- DML practice: use a transaction to test changes safely.
BEGIN;
INSERT INTO customers (first_name,last_name,email,city,state)
VALUES ('Demo','User','demo.user@example.com','Chennai','Tamil Nadu')
RETURNING *;

UPDATE customers
SET city = 'Coimbatore'
WHERE email = 'demo.user@example.com'
RETURNING customer_id, email, city;

SELECT * FROM customers WHERE email = 'demo.user@example.com';

DELETE FROM customers
WHERE email = 'demo.user@example.com'
RETURNING customer_id, email;
ROLLBACK;
-- ROLLBACK means the demo insert/update/delete are not persisted.
