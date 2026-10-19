# Pattern Identification Report — Template

## Dataset and scope
- Dataset:
- Date range / sample size:
- Question being investigated:
- Fields used:

## Findings
For each finding, document:
1. **Observation:** What pattern was seen?
2. **Evidence:** Metric, sample size, plot/table, and method.
3. **Interpretation:** What might explain the pattern?
4. **Caveat:** Missing data, outliers, small groups, confounding, or multiple comparisons.
5. **Next action:** Validation, deeper analysis, or pipeline rule.

## Required pattern checks
- [ ] Overall trend and rolling summary (time series)
- [ ] Weekday/month seasonality (time series)
- [ ] Correlations with sample size and caveats
- [ ] Potential anomalies and review notes
- [ ] Segment-level differences
- [ ] Missingness and duplicate patterns
- [ ] Invalid values against business rules
- [ ] Data drift / collection changes if historical data is available

## Statistical interpretation
- Define null and alternative hypotheses before testing.
- Report test, sample sizes, test statistic, p-value, and effect size when available.
- Use a significance threshold chosen before analysis (commonly 0.05).
- Statistical significance does not imply practical importance or causation.
- If many hypotheses are tested, consider multiple-testing correction.
