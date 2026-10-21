-- DDL practice: run independently and inspect the effect.
CREATE TABLE ddl_demo (
    demo_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    label TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE ddl_demo ADD COLUMN is_complete BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE ddl_demo RENAME COLUMN label TO description;
-- DROP TABLE ddl_demo; -- Uncomment only when you want to remove this practice table.
