# SQL quick reference (PostgreSQL)

## DDL — define objects
- `CREATE TABLE ...` creates a table.
- `ALTER TABLE ... ADD COLUMN ...` changes a table.
- `DROP TABLE ...` removes a table and its data.
- Constraints: `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`, `CHECK`.

## DML — change data
- `INSERT INTO table (columns) VALUES (...) RETURNING *;`
- `UPDATE table SET column = value WHERE condition RETURNING *;`
- `DELETE FROM table WHERE condition RETURNING *;`
- Always inspect the `WHERE` clause before UPDATE or DELETE.

## Querying
- `SELECT columns FROM table WHERE condition`
- `ORDER BY column DESC LIMIT n`
- `DISTINCT` removes duplicate result rows.
- `LIKE` is pattern matching; `ILIKE` is case-insensitive matching in PostgreSQL.
- `IN (...)`, `BETWEEN lower AND upper`, `IS NULL`.
- `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` are aggregate functions.
- `GROUP BY` creates groups; `HAVING` filters groups.
- `JOIN` combines related rows.
- `WITH` defines a common table expression.
- Window functions such as `ROW_NUMBER`, `RANK`, `LAG` operate across related rows.

## Transactions and performance
- `BEGIN; ... COMMIT;` persists a transaction.
- `ROLLBACK;` cancels uncommitted changes.
- `EXPLAIN ANALYZE` runs the query and reports actual execution measurements; use caution with modifying statements.
- Indexes speed up some access patterns but add storage and write overhead.
