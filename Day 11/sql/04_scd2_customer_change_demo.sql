-- SCD Type 2 snapshot apply. Tracked attributes: city, state, segment.
-- Type 1 attributes in this example: full_name, email (overwrite across history).
BEGIN;

-- Close current version only when a tracked attribute changed and timestamp advances.
UPDATE dim_customer d SET valid_to=s.updated_at, is_current=FALSE
FROM (SELECT DISTINCT ON(customer_id) * FROM stg_customer_changes
      ORDER BY customer_id, updated_at DESC) s
WHERE d.customer_id=s.customer_id AND d.is_current=TRUE
 AND (d.city IS DISTINCT FROM s.city OR d.state IS DISTINCT FROM s.state OR d.segment IS DISTINCT FROM s.segment)
 AND s.updated_at > d.valid_from;

-- Insert a new current version for changed customers and new natural keys.
-- The partial unique index protects against multiple current rows.
INSERT INTO dim_customer(customer_id, full_name, email, city, state, segment,
                         valid_from, valid_to, is_current, version_number, source_updated_at)
SELECT s.customer_id, s.full_name, s.email, s.city, s.state, s.segment,
       s.updated_at, TIMESTAMP '9999-12-31 00:00:00', TRUE,
       COALESCE((SELECT MAX(h.version_number)+1 FROM dim_customer h WHERE h.customer_id=s.customer_id),1),
       s.updated_at
FROM (SELECT DISTINCT ON(customer_id) * FROM stg_customer_changes
      ORDER BY customer_id, updated_at DESC) s
LEFT JOIN dim_customer cur ON cur.customer_id=s.customer_id AND cur.is_current=TRUE
WHERE cur.customer_sk IS NULL
   OR (cur.city IS DISTINCT FROM s.city OR cur.state IS DISTINCT FROM s.state OR cur.segment IS DISTINCT FROM s.segment)
ON CONFLICT(customer_id, version_number) DO NOTHING;

-- Deliberate Type 1 example: correct name/email on all historical versions.
UPDATE dim_customer d SET full_name=s.full_name, email=s.email
FROM (SELECT DISTINCT ON(customer_id) * FROM stg_customer_changes
      ORDER BY customer_id, updated_at DESC) s
WHERE d.customer_id=s.customer_id
  AND (d.full_name IS DISTINCT FROM s.full_name OR d.email IS DISTINCT FROM s.email);

COMMIT;

SELECT customer_id, customer_sk, full_name, city, state, segment,
       valid_from, valid_to, is_current, version_number
FROM dim_customer ORDER BY customer_id, version_number;
