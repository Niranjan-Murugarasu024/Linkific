# Day 9 — Advanced SQL with PostgreSQL

## Deliverables
- 45 advanced queries in `sql/02_advanced_queries.sql`.
- JOIN lab for INNER, LEFT, RIGHT, FULL OUTER, CROSS, and self joins.
- Window function lab covering ROW_NUMBER, RANK, DENSE_RANK, PARTITION BY, running totals, LAG, LEAD, and moving averages.
- Subqueries, correlated subqueries, multiple CTEs, recursive CTEs, ROLLUP, CUBE, and time-based aggregation.
- Query optimization lab using EXPLAIN ANALYZE and indexes.
- SQL patterns reference in `docs/sql_patterns.md`.

## Prerequisite
This project uses the `ecommerce_practice` database from Day 8. It does not recreate the base tables. If you have not completed Day 8, first create the customers, categories, products, orders, order_items, and payments tables and load sample data.

## Execute in pgAdmin 4
1. Connect to PostgreSQL and select `ecommerce_practice`.
2. Open Query Tool.
3. Run `sql/01_setup_and_views.sql` once.
4. Run `sql/03_join_lab.sql` and inspect row differences between joins.
5. Run `sql/04_window_functions_lab.sql`.
6. Execute `sql/02_advanced_queries.sql` section by section.
7. Run `sql/05_optimization_lab.sql` and note scan type, estimated/actual rows, and buffers.
8. Review `docs/sql_patterns.md`.

## Notes
- PostgreSQL 12+; PostgreSQL 15+ recommended.
- ROLLUP, CUBE, FILTER, DISTINCT ON, and ILIKE are PostgreSQL syntax.
- Query plan choices depend on PostgreSQL version, table size, and statistics.
- The sample data is intentionally small. Payment reconciliation may show mismatches because example payment amounts are illustrative.
