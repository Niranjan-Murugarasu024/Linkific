# SQL & PostgreSQL E-commerce Practice Project

A beginner-to-intermediate SQL project designed for Data Engineering practice.

## Learning outcomes
- Set up PostgreSQL and connect with pgAdmin 4.
- Create relational tables with keys and constraints.
- Perform INSERT, SELECT, UPDATE, DELETE, and `RETURNING`.
- Practice filtering, sorting, aggregation, joins, subqueries, CTEs, and window functions.
- Create indexes and inspect query plans.

## Requirements
- PostgreSQL 15+ (PostgreSQL 16 or 17 recommended)
- pgAdmin 4 or DBeaver

## Windows setup
1. Install PostgreSQL using the official installer and remember the password you set for the `postgres` role.
2. Open pgAdmin 4 and connect to your local PostgreSQL server.
3. Open Query Tool while connected to the default `postgres` database.
4. Run `sql/01_create_database.sql` once. `CREATE DATABASE` must run outside a transaction.
5. In pgAdmin, connect to the new `ecommerce_practice` database.
6. Run these scripts in order:
   - `sql/02_create_tables.sql`
   - `sql/03_constraints_indexes.sql`
   - `sql/04_insert_sample_data.sql`
7. Execute `sql/07_query_fundamentals.sql` for 60 practice queries. Read comments before running the mutation examples numbered 51–54.
8. Use `sql/05_ddl_practice.sql`, `sql/06_dml_practice.sql`, `sql/08_aggregate_queries.sql`, `sql/09_advanced_practice.sql`, and `sql/10_solutions.sql` as separate exercises.

## PowerShell folder setup
```powershell
New-Item -ItemType Directory -Force -Path "E:\SQL-PostgreSQL-Project\sql"
New-Item -ItemType Directory -Force -Path "E:\SQL-PostgreSQL-Project\data"
New-Item -ItemType Directory -Force -Path "E:\SQL-PostgreSQL-Project\docs"
Set-Location "E:\SQL-PostgreSQL-Project"
```

Extract the ZIP into `E:\SQL-PostgreSQL-Project` if you download the provided archive.

## Data model
Customers place orders. Orders contain order items, each referring to a product. Products belong to categories. Payments are associated with orders, and inventory movements record stock changes.

## Important notes
- Sample data is fictional.
- The sample database is intentionally small; index-performance results will not be representative of a large production workload.
- The schema is for learning, not production payment processing or accounting.
- Avoid running destructive statements against databases containing data you need.
