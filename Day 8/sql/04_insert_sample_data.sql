INSERT INTO categories (category_name, description) VALUES
('Electronics','Devices and accessories'),
('Books','Printed and digital learning materials'),
('Home','Home and kitchen essentials'),
('Fitness','Exercise and wellness products'),
('Stationery','Writing and office supplies');

INSERT INTO customers (first_name,last_name,email,phone,city,state) VALUES
('Aarav','Sharma','aarav.sharma@example.com','9000000001','Chennai','Tamil Nadu'),
('Diya','Iyer','diya.iyer@example.com','9000000002','Coimbatore','Tamil Nadu'),
('Kabir','Rao','kabir.rao@example.com','9000000003','Bengaluru','Karnataka'),
('Meera','Nair','meera.nair@example.com','9000000004','Kochi','Kerala'),
('Arjun','Patel','arjun.patel@example.com','9000000005','Mumbai','Maharashtra'),
('Ananya','Das','ananya.das@example.com','9000000006','Kolkata','West Bengal'),
('Ishaan','Reddy','ishaan.reddy@example.com','9000000007','Hyderabad','Telangana'),
('Sana','Khan','sana.khan@example.com','9000000008','Pune','Maharashtra'),
('Vikram','Menon','vikram.menon@example.com','9000000009','Coimbatore','Tamil Nadu'),
('Priya','Joshi','priya.joshi@example.com','9000000010','Delhi','Delhi');

INSERT INTO products (category_id,product_name,sku,unit_price,stock_quantity) VALUES
(1,'Wireless Mouse','ELEC-001',799.00,120),
(1,'Mechanical Keyboard','ELEC-002',3499.00,45),
(1,'USB-C Hub','ELEC-003',1899.00,60),
(1,'Bluetooth Headphones','ELEC-004',2499.00,35),
(1,'27-inch Monitor','ELEC-005',15999.00,18),
(2,'SQL for Beginners','BOOK-001',499.00,100),
(2,'Python Data Engineering','BOOK-002',799.00,70),
(2,'Database Design Handbook','BOOK-003',999.00,40),
(3,'Desk Lamp','HOME-001',1199.00,55),
(3,'Water Bottle','HOME-002',399.00,150),
(3,'Ergonomic Chair','HOME-003',8999.00,12),
(4,'Yoga Mat','FIT-001',899.00,65),
(4,'Resistance Bands','FIT-002',599.00,80),
(4,'Dumbbell Pair','FIT-003',1999.00,25),
(5,'Notebook Pack','STAT-001',249.00,200),
(5,'Gel Pen Set','STAT-002',199.00,180);

INSERT INTO orders (customer_id,order_date,status,shipping_city,shipping_state,notes) VALUES
(1,'2026-01-10 10:15:00+05:30','delivered','Chennai','Tamil Nadu',NULL),
(2,'2026-01-12 14:30:00+05:30','delivered','Coimbatore','Tamil Nadu',NULL),
(3,'2026-01-15 09:20:00+05:30','shipped','Bengaluru','Karnataka',NULL),
(1,'2026-02-02 16:45:00+05:30','delivered','Chennai','Tamil Nadu','Gift order'),
(4,'2026-02-07 11:00:00+05:30','cancelled','Kochi','Kerala',NULL),
(5,'2026-02-18 18:10:00+05:30','paid','Mumbai','Maharashtra',NULL),
(6,'2026-03-01 12:05:00+05:30','processing','Kolkata','West Bengal',NULL),
(7,'2026-03-04 19:40:00+05:30','delivered','Hyderabad','Telangana',NULL),
(8,'2026-03-12 08:50:00+05:30','pending','Pune','Maharashtra',NULL),
(9,'2026-03-15 13:25:00+05:30','delivered','Coimbatore','Tamil Nadu',NULL),
(10,'2026-04-01 17:00:00+05:30','refunded','Delhi','Delhi',NULL),
(2,'2026-04-05 10:35:00+05:30','shipped','Coimbatore','Tamil Nadu',NULL),
(3,'2026-04-10 15:55:00+05:30','delivered','Bengaluru','Karnataka',NULL),
(5,'2026-04-18 20:15:00+05:30','paid','Mumbai','Maharashtra',NULL),
(1,'2026-05-02 09:05:00+05:30','pending','Chennai','Tamil Nadu',NULL);

INSERT INTO order_items (order_id,product_id,quantity,unit_price) VALUES
(1,1,2,799.00),(1,6,1,499.00),
(2,7,1,799.00),(2,15,3,249.00),
(3,2,1,3499.00),(3,3,1,1899.00),
(4,5,1,15999.00),(4,4,1,2499.00),
(5,12,2,899.00),
(6,11,1,8999.00),(6,10,2,399.00),
(7,8,1,999.00),(7,6,2,499.00),
(8,14,1,1999.00),(8,13,2,599.00),
(9,3,1,1899.00),
(10,9,1,1199.00),(10,10,2,399.00),(10,16,2,199.00),
(11,5,1,15999.00),
(12,2,1,3499.00),(12,7,1,799.00),
(13,4,1,2499.00),(13,6,2,499.00),
(14,1,1,799.00),(14,15,5,249.00),
(15,12,1,899.00);

INSERT INTO payments (order_id,amount,payment_method,payment_status,transaction_reference) VALUES
(1,2097.00,'upi','successful','TXN-1001'),
(2,1546.00,'card','successful','TXN-1002'),
(3,5398.00,'card','successful','TXN-1003'),
(4,18498.00,'upi','successful','TXN-1004'),
(5,1798.00,'wallet','failed','TXN-1005'),
(6,9797.00,'net_banking','successful','TXN-1006'),
(7,1997.00,'upi','successful','TXN-1007'),
(8,3197.00,'card','successful','TXN-1008'),
(9,1899.00,'upi','pending','TXN-1009'),
(10,2395.00,'cash_on_delivery','successful','TXN-1010'),
(11,15999.00,'card','refunded','TXN-1011'),
(12,4298.00,'upi','successful','TXN-1012'),
(13,3497.00,'card','successful','TXN-1013'),
(14,2044.00,'wallet','successful','TXN-1014'),
(15,899.00,'upi','pending','TXN-1015');

INSERT INTO inventory_movements (product_id,quantity_change,reason,notes) VALUES
(1,100,'restock','Initial stock'),(1,-2,'sale','Sample order'),
(2,50,'restock','Initial stock'),(2,-1,'sale','Sample order'),
(6,100,'restock','Initial stock'),(6,-1,'sale','Sample order'),
(12,70,'restock','Initial stock'),(12,-2,'sale','Sample order');
