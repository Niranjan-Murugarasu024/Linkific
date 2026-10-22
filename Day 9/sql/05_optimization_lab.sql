-- Inspect actual plan, scan type, estimated vs actual rows, and buffer metrics.
EXPLAIN (ANALYZE,BUFFERS)
SELECT order_id,order_date,status FROM orders WHERE customer_id=1 ORDER BY order_date DESC;

-- Review current indexes.
SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY tablename,indexname;

-- Refresh planner statistics after significant data changes.
ANALYZE orders;
ANALYZE order_items;
ANALYZE products;

-- Re-run EXPLAIN ANALYZE and compare. Small tables may favor sequential scans.
