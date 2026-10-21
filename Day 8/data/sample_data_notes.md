# Sample data

The `04_insert_sample_data.sql` script inserts fictional customers, products, categories, orders, order items, payments, and inventory movements. Email addresses use `example.com`; phone numbers are placeholders. Do not treat the sample as real customer information.

Load order:
1. `02_create_tables.sql`
2. `03_constraints_indexes.sql`
3. `04_insert_sample_data.sql`

The dataset is deliberately small enough to inspect manually. For meaningful index benchmarking, generate a larger dataset and compare `EXPLAIN (ANALYZE, BUFFERS)` results before and after index creation.
