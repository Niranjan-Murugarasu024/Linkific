# Day 20 — Synthetic Data Generation with Python Faker

A practical project for generating realistic, relational test data for three domains:
1. E-commerce (customers, products, orders, order items, transactions)
2. HR (departments, employees, attendance, payroll)
3. Financial transactions (accounts, customers, transactions)

The generators use Faker, deterministic seeds, realistic date ranges, logical constraints, and PostgreSQL-compatible CSV exports. The default run creates 100,000 e-commerce orders and supporting records; choose a smaller row count for a quick test.

## Requirements
- Python 3.10+
- PostgreSQL 14+ (optional; CSV generation works without it)

## Setup (Windows PowerShell)
```powershell
cd day20_synthetic_data_project
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Generate datasets
Quick test:
```powershell
python -m src.generate_all --orders 1000 --employees 100 --financial-transactions 5000
```

Full deliverable (100k orders):
```powershell
python -m src.generate_all --orders 100000 --employees 1000 --financial-transactions 100000
```

Output is written to `data/generated/` as CSV. Each database has a schema SQL file in `sql/`.
- E-commerce: customers, products, orders, order_items, payments
- HR: departments, employees, attendance, payroll
- Finance: customers, accounts, transactions

## Load into PostgreSQL
Create a database (example):
```sql
CREATE DATABASE synthetic_lab;
```
Set connection values in `.env`, then:
```powershell
python -m src.load_postgres --database synthetic_lab
```
The loader creates tables from `sql/schema.sql` and uses PostgreSQL `COPY` for efficient bulk loading. It loads each CSV into its matching table. If you use a different database name, pass it with `--database`.

## Validation
```powershell
python -m src.validate_data
```
Validation checks:
- primary key uniqueness
- foreign key references
- order item quantity and amount constraints
- order/payment date ordering
- HR attendance/payroll references
- finance account/customer references and nonnegative amounts

## Important design choices
- IDs are generated as stable integer keys and relationships are built from those IDs.
- Order and payment dates are bounded to the configured period.
- Payment amount equals order total; order total equals the sum of its items.
- HR salary and payroll amounts are positive; attendance dates are not in the future.
- Finance transactions reference valid accounts and have nonnegative amounts.
- Faker seed makes results reproducible for the same options.
- This is synthetic data only; names, emails, companies and addresses are fictional. Do not use generated records as real customer or financial data.

## Project layout
```text
day20_synthetic_data_project/
├── data/generated/       # generated CSV files
├── sql/schema.sql       # PostgreSQL tables/indexes
├── src/
│   ├── common.py
│   ├── ecommerce.py
│   ├── hr.py
│   ├── finance.py
│   ├── generate_all.py
│   ├── load_postgres.py
│   └── validate_data.py
├── .env.example
├── requirements.txt
└── README.md
```
