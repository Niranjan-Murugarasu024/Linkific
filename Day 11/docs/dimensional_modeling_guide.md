# Dimensional Modeling Guide

## Warehouse fundamentals
- **OLTP** systems serve operational transactions (create order, update address) and emphasize integrity and efficient writes; schemas are often normalized.
- **OLAP** systems answer analytical questions over large historical datasets (revenue by month, cohort trends) and favor scans, aggregations, and dimensional access patterns.
- A **database** is a broad storage system; a **data warehouse** integrates governed historical data for analysis; a **data mart** is a focused analytical area such as sales or finance.
- Common flow: source systems → ingestion/staging → cleaning/quality checks → warehouse facts/dimensions → semantic/reporting layer → analytics.
- **ETL** transforms before loading the target; **ELT** loads data first and transforms inside the analytical platform. Batch, streaming, and hybrid architectures are all possible.

## Dimensional modeling concepts
- **Fact table:** business events or measurements, with dimension keys and measures.
- **Dimension table:** descriptive context used to filter, group, and label facts.
- **Grain:** exactly what one row represents; declare it before designing columns.
- **Additive measure:** sums meaningfully across dimensions (e.g., units sold).
- **Semi-additive:** sums across some dimensions but not time (e.g., account balance).
- **Non-additive:** ratios/percentages; recompute from underlying totals rather than summing.
- **Surrogate key:** warehouse-controlled identifier. **Natural/business key:** source identifier such as `customer_id`.
- **Conformed dimension:** shared dimension with the same definition across facts/marts.
- **Degenerate dimension:** transaction identifier kept on the fact, such as `order_id`, without a separate dimension table.

## Star vs snowflake vs galaxy
- **Star:** one fact links directly to descriptive dimensions; easy to query and understand.
- **Snowflake:** dimension attributes are further normalized into sub-dimensions (e.g., product → category); fewer repeated attributes may be offset by added joins/complexity.
- **Galaxy/fact constellation:** several fact tables share conformed dimensions; each fact must have its own grain. Aggregate facts separately before combining to prevent fan-out and double counting.

## The implemented sales star schema
**Grain:** one row per `(order_id, order_line_id)`.

**Measures:** `quantity`, `gross_amount = quantity × unit_price`, `discount_amount`, and `net_amount = gross_amount − discount_amount`. The source data guarantees discount is not greater than gross.

**Dimensions:**
- `dim_date`: date hierarchy (year → quarter → month → day).
- `dim_customer`: customer descriptors. City, state, segment use SCD2 in this lab.
- `dim_product`: product descriptors; Type 1 overwrite in this lab.
- `dim_channel`: online/store/partner.

The fact uses `customer_sk`, not just the natural `customer_id`, so older sales can refer to the precise customer version valid on the sales date.

## SCD Type 1, 2, 3
- **Type 1 — overwrite:** replace an attribute value and lose its previous value. Useful for corrections or fields where history is not required.
- **Type 2 — new row:** close the old row and insert a new version with a new surrogate key. This project uses `valid_from`, `valid_to`, `is_current`, and `version_number`. Validity is start-inclusive/end-exclusive `[valid_from, valid_to)`, so adjacent windows can meet exactly.
- **Type 3 — previous-value column:** store a limited prior state (e.g., `current_segment`, `previous_segment`). It is not a full change history.

Different attributes can have different policies. This example tracks city/state/segment as Type 2, and overwrites name/email as Type 1. That is a deliberate business rule, not a universal rule.

## SCD2 flow
1. Deduplicate the incoming snapshot by business key.
2. Match it to the current dimension row.
3. Compare only historized attributes, with null-safe comparisons.
4. If a tracked value changed and its effective timestamp is later, close the existing version.
5. Insert a new row with a new surrogate key and incremented version number.
6. Resolve fact rows using natural key plus event time (`event_time >= valid_from AND event_time < valid_to`).

## Production considerations
Late/out-of-order change events, source deletions, timestamp precision, concurrent batch runs, transactional handling, audit columns, ingestion IDs, unknown members, late-arriving facts, timezone normalization, source reconciliation, and CDC/watermark strategy require explicit design. This project's scripts favor teaching clarity and are not a complete production CDC framework.

## Quality rules
1. At most one current version for each customer natural key.
2. Type 2 windows for one customer must not overlap.
3. Every fact key resolves to one dimension version.
4. `gross_amount = quantity * unit_price`.
5. `net_amount = gross_amount - discount_amount`.
6. Discount is nonnegative and does not exceed gross.
7. `(order_id, order_line_id)` is unique.
