# Day 9 Advanced SQL Patterns

## JOINs
- INNER JOIN: only matching rows.
- LEFT JOIN: all left rows plus matches; missing right-side values are NULL.
- RIGHT JOIN: all right rows; often rewritten as LEFT JOIN for readability.
- FULL OUTER JOIN: matched and unmatched rows from both sides.
- CROSS JOIN: Cartesian product; output row count is left count × right count.
- Self join: a table joined to itself using aliases.
- Multiple joins: follow foreign-key relationships and check for accidental row multiplication.

## Aggregation
- WHERE filters rows before grouping; HAVING filters groups after aggregation.
- COUNT(DISTINCT x) counts unique non-NULL values.
- ROLLUP creates hierarchical subtotals; CUBE creates combinations of grouping subtotals.
- FILTER (WHERE ...) supports conditional aggregation.

## Window functions
- ROW_NUMBER assigns sequential row numbers within a window.
- RANK leaves gaps after ties; DENSE_RANK does not.
- PARTITION BY restarts calculations for each group.
- SUM(x) OVER (ORDER BY ...) supports running totals; specify a frame for predictable behavior.
- LAG and LEAD access previous/next rows.
- Moving average example: AVG(x) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW).

## Subqueries and CTEs
- Scalar subqueries return one value.
- EXISTS and NOT EXISTS test matching-row existence.
- Correlated subqueries reference the outer query.
- CTEs (WITH) name intermediate query results.
- Recursive CTEs combine an anchor query with a recursive term for sequences and hierarchies.

## Query optimization
- EXPLAIN shows estimated plan; EXPLAIN ANALYZE executes and reports actual metrics.
- Inspect estimated versus actual rows, scan types, join strategy, sorts, and buffers.
- Index columns used frequently for joins, selective filters, or ordering when justified by workload.
- Indexes consume storage and add write overhead; they do not always improve performance.
- Use realistic data volumes. A tiny practice database cannot demonstrate production performance reliably.
