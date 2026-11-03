# Data Collection Plan

## 1. Data types
**Primary data:** collected directly for this research, such as a questionnaire administered to eligible online shoppers.

**Secondary data:** existing sources collected for another purpose, such as published studies, public reports, or anonymized platform-level datasets. Verify licensing, provenance, definitions, and suitability.

## 2. Target population and eligibility
- Adults aged 18 or older.
- Purchased from an e-commerce platform in the previous six months.
- Able to understand the survey language and provide informed consent.

Define incomplete-response exclusion rules before analysis. Do not exclude respondents because their answers disagree with the hypothesis.

## 3. Sampling strategy
Preferred for a stronger study: probability sampling from an appropriate sampling frame, if available and ethically authorized.

Practical student alternative: convenience sampling with transparent reporting. Recruit through approved channels and avoid pressure.

### Sample size
Do not choose sample size only for convenience. For a real study, calculate it based on the primary outcome, expected effect, alpha (often 0.05), power (often 0.80 or 0.90), test, and expected nonresponse. Document assumptions. The 120 included records are synthetic and are not a sample-size recommendation.

## 4. Survey administration
1. Show participant information and consent.
2. Confirm eligibility.
3. Ask recent purchase behavior.
4. Present satisfaction and repeat-intention items.
5. Keep demographic questions minimal and optional.
6. Do not collect direct identifiers.
7. Pilot for clarity and completion time.
8. Store data with restricted access.
9. Define cleaning rules before hypothesis analysis.

## 5. Data dictionary
| Variable | Type | Description |
|---|---|---|
| respondent_id | string | Synthetic study identifier |
| age_band | categorical | Fictional age category |
| purchase_frequency | categorical | Fictional online purchase frequency |
| satisfaction | integer 1–5 | Overall satisfaction rating |
| repeat_intention | integer 1–5 | Stated likelihood of buying again |
| delivery_rating | integer 1–5 | Delivery experience rating |
| consent | boolean | Synthetic consent flag |

## 6. Quality checks
- Likert values within 1–5.
- Check duplicates and missing values.
- Confirm eligibility and consent for real data.
- Use a consistent missing-data rule.
- Keep raw data read-only and cleaned data separate.
- Document transformations.

## 7. Ethics and privacy
Voluntary participation; clear consent; no names, emails, phone numbers, addresses, order IDs, or payment details; explain purpose, use, retention, and withdrawal; restrict access; use secure storage; follow institutional and applicable privacy rules. Do not claim approval unless obtained.
