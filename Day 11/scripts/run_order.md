# Execution order

1. Create `sales_warehouse_lab`.
2. Run `sql/01_create_warehouse.sql`.
3. Run `sql/02_create_staging.sql`.
4. Import the four CSV files into their matching staging tables; see README.
5. Run `sql/03_load_dimensions_and_facts.sql`.
6. Inspect the star schema and run `sql/05_analytics_queries.sql`.
7. Run `sql/06_validation_checks.sql`.
8. Run `sql/04_scd2_customer_change_demo.sql` to apply the later customer snapshot.
9. Re-run analytics and validation, and explain the customer history.

For a clean replay, use a fresh lab database and reimport the CSVs. Do not duplicate staging data by importing the same CSV repeatedly.
