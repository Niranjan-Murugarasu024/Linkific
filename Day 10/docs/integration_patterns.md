# Python + PostgreSQL Integration Patterns

## psycopg2
Use `psycopg2.connect()` for direct driver access. Bind values with `%s` placeholders and pass a tuple; do not interpolate untrusted values into SQL. Connection context managers commit on success and roll back on exceptions.

## Pandas
- `pd.read_sql_query(query, connection)` returns a DataFrame.
- `chunksize=1000` returns an iterator of DataFrame chunks for large results.
- `DataFrame.to_sql()` writes data through SQLAlchemy.
- `read_sql_table()` reflects an existing table through SQLAlchemy where supported.
- Validate data types and nulls before loading.

## SQLAlchemy
Use `create_engine()` for connection pooling, `text()` for parameterized SQL, and `engine.begin()` for transaction scopes. ORM classes map Python objects to existing database tables. This project intentionally does not call `Base.metadata.create_all()` against your existing Day 8 schema.

## ETL
Extract → validate/transform → load. Check HTTP status and response shape, use timeouts, log counts, and keep database writes transactional. The API example uses `ON CONFLICT` to make repeated loads idempotent.

## Incremental loading caveat
The sample uses increasing `order_id` as a watermark. This detects new IDs but does not detect updates to older orders. Production pipelines should use a reliable `updated_at` column, CDC, and/or reconciliation for late-arriving records and deletions.

## Security
Never commit `.env` or real credentials. Parameterize values. SQL identifiers such as table names generally cannot be passed as normal bind parameters; use a strict allowlist if dynamic identifiers are needed.
