CREATE TABLE IF NOT EXISTS ecommerce_customers (
 customer_id BIGINT PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT UNIQUE, phone TEXT,
 city TEXT, country TEXT, created_at DATE);
CREATE TABLE IF NOT EXISTS ecommerce_products (
 product_id BIGINT PRIMARY KEY, product_name TEXT, category TEXT, unit_price NUMERIC(12,2), stock INT);
CREATE TABLE IF NOT EXISTS ecommerce_orders (
 order_id BIGINT PRIMARY KEY, customer_id BIGINT REFERENCES ecommerce_customers(customer_id),
 order_date DATE, status TEXT, total_amount NUMERIC(14,2));
CREATE TABLE IF NOT EXISTS ecommerce_order_items (
 order_item_id BIGINT PRIMARY KEY, order_id BIGINT REFERENCES ecommerce_orders(order_id),
 product_id BIGINT REFERENCES ecommerce_products(product_id), quantity INT, unit_price NUMERIC(12,2), line_total NUMERIC(14,2));
CREATE TABLE IF NOT EXISTS ecommerce_payments (
 payment_id BIGINT PRIMARY KEY, order_id BIGINT REFERENCES ecommerce_orders(order_id),
 payment_date DATE, method TEXT, amount NUMERIC(14,2), payment_status TEXT);
CREATE TABLE IF NOT EXISTS hr_departments (department_id INT PRIMARY KEY, department_name TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS hr_employees (
 employee_id BIGINT PRIMARY KEY, department_id INT REFERENCES hr_departments(department_id),
 first_name TEXT, last_name TEXT, email TEXT UNIQUE, job_title TEXT, hire_date DATE,
 annual_salary NUMERIC(14,2), employment_status TEXT);
CREATE TABLE IF NOT EXISTS hr_attendance (
 attendance_id BIGINT PRIMARY KEY, employee_id BIGINT REFERENCES hr_employees(employee_id), attendance_date DATE, status TEXT);
CREATE TABLE IF NOT EXISTS hr_payroll (
 payroll_id BIGINT PRIMARY KEY, employee_id BIGINT REFERENCES hr_employees(employee_id),
 pay_period TEXT, gross_pay NUMERIC(14,2), deductions NUMERIC(14,2), net_pay NUMERIC(14,2));
CREATE TABLE IF NOT EXISTS finance_customers (
 fin_customer_id BIGINT PRIMARY KEY, full_name TEXT, email TEXT UNIQUE, country TEXT, created_date DATE);
CREATE TABLE IF NOT EXISTS finance_accounts (
 account_id BIGINT PRIMARY KEY, fin_customer_id BIGINT REFERENCES finance_customers(fin_customer_id),
 account_type TEXT, currency TEXT, opening_balance NUMERIC(14,2));
CREATE TABLE IF NOT EXISTS finance_transactions (
 transaction_id BIGINT PRIMARY KEY, account_id BIGINT REFERENCES finance_accounts(account_id),
 transaction_date DATE, transaction_type TEXT, amount NUMERIC(14,2), merchant TEXT,
 description TEXT, channel TEXT, status TEXT);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON ecommerce_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON ecommerce_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_items_order ON ecommerce_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON ecommerce_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_hr_employee_department ON hr_employees(department_id);
CREATE INDEX IF NOT EXISTS idx_attendance_employee_date ON hr_attendance(employee_id,attendance_date);
CREATE INDEX IF NOT EXISTS idx_finance_account ON finance_transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_finance_date ON finance_transactions(transaction_date);
