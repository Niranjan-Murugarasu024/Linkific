# Practice: Alternative Warehouse Designs

## Sales galaxy / fact constellation
Business questions: monthly net sales by category/channel; returns by reason; customer segments over time.
- `fact_sales`: one row per order line; measures quantity, gross, discount, net.
- `fact_returns`: one row per return line; measures returned quantity and refund amount.
- Conformed dimensions: `dim_date`, `dim_product`, `dim_customer`, `dim_channel`; add `dim_return_reason` for the return fact.
- A product/date can appear in many sales rows and many return rows. Do not join both raw facts and sum directly; aggregate each to a compatible grain before combining.

## Healthcare warehouse design exercise (synthetic/de-identified data only)
Possible questions: encounter volume by month/department, wait time distributions, readmission trends by age band, lab orders by test category.

Candidate facts and grains:
- `fact_encounter`: one row per patient encounter; e.g. wait minutes, length of stay, allowed amount.
- `fact_lab_result`: one row per lab-result observation; numeric result only with test and unit context, abnormal indicator.
- `fact_medication_administration`: one row per administration event; dose and unit-aware amount.
- `fact_claim_line`: one row per claim line; billed/allowed/paid measures.

Candidate dimensions: `dim_patient`, `dim_provider`, `dim_department`, `dim_date`, `dim_diagnosis`, `dim_procedure`, `dim_test`, `dim_payer`, `dim_location`. Multiple diagnoses per encounter may need a bridge table with explicit allocation rules if measures are aggregated through it.

Healthcare cautions: measurements of different tests/units are not directly comparable; distinguish event time from ingestion time; govern identity, de-identification, minimum-necessary access, audit, retention, and source-code/version history. Do not use real patient data in this practice project.

## SCD Type 3 mini-exercise
Create `current_segment` and `previous_segment`. On a segment change, move current to previous and write the incoming segment to current. Explain why this records only one prior state, unlike Type 2's full version history.

## Design review checklist
For every fact, state the grain, business process, measures and additivity, dimensions, surrogate/natural keys, SCD policy per attribute, late-arrival policy, validation checks, and reconciliation totals.
