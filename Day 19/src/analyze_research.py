"""Day 19 research analysis. Run: python src/analyze_research.py"""
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ecommerce_satisfaction_sample.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
df = pd.read_csv(DATA)

required = {"respondent_id","age_band","purchase_frequency","satisfaction","repeat_intention","delivery_rating","consent"}
missing_cols = required - set(df.columns)
if missing_cols:
    raise ValueError(f"Missing required columns: {sorted(missing_cols)}")

for col in ["satisfaction","repeat_intention","delivery_rating"]:
    if not df[col].dropna().between(1,5).all():
        raise ValueError(f"{col} contains values outside 1–5")

numeric = ["satisfaction","repeat_intention","delivery_rating"]
descriptive = df[numeric].describe().T
descriptive["missing_count"] = df[numeric].isna().sum()
descriptive.to_csv(OUT / "descriptive_statistics.csv")

for col in ["age_band","purchase_frequency"]:
    df[col].value_counts(dropna=False).rename_axis(col).to_frame("count").to_csv(OUT / f"{col}_frequency.csv")

valid = df[["satisfaction","repeat_intention"]].dropna()
corr = stats.pearsonr(valid["satisfaction"], valid["repeat_intention"])

# Demonstration cutoff: <=3 lower satisfaction; >=4 higher satisfaction.
df["satisfaction_group"] = np.where(df["satisfaction"] <= 3, "Lower (<=3)", "Higher (>=4)")
lower = df.loc[df["satisfaction_group"] == "Lower (<=3)", "repeat_intention"].dropna()
higher = df.loc[df["satisfaction_group"] == "Higher (>=4)", "repeat_intention"].dropna()
welch = stats.ttest_ind(higher, lower, equal_var=False, alternative="two-sided")

n1, n2 = len(higher), len(lower)
s1, s2 = higher.std(ddof=1), lower.std(ddof=1)
pooled_sd = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2)/(n1+n2-2))
cohen_d = (higher.mean()-lower.mean())/pooled_sd if pooled_sd else np.nan

summary = {
 "dataset_note":"Synthetic practice data; not real customer evidence.",
 "n_total":int(len(df)), "n_valid_correlation":int(len(valid)),
 "pearson_r":float(corr.statistic), "pearson_p_value":float(corr.pvalue),
 "lower_group_n":int(n2), "lower_group_mean":float(lower.mean()),
 "higher_group_n":int(n1), "higher_group_mean":float(higher.mean()),
 "welch_t_statistic":float(welch.statistic), "welch_p_value":float(welch.pvalue),
 "cohen_d_higher_minus_lower":float(cohen_d), "alpha":0.05
}
pd.Series(summary, name="value").to_csv(OUT / "analysis_summary.csv")
decision = "statistically significant at alpha=0.05" if welch.pvalue < 0.05 else "not statistically significant at alpha=0.05"
report = f"""DAY 19 — RESEARCH ANALYSIS REPORT
================================
Dataset: synthetic educational data; no real customers are represented.
Research question: Is satisfaction associated with repeat-purchase intention?

Sample size: {len(df)}
Valid correlation pairs: {len(valid)}

DESCRIPTIVES
Satisfaction mean: {df['satisfaction'].mean():.3f}
Repeat intention mean: {df['repeat_intention'].mean():.3f}
Delivery rating mean: {df['delivery_rating'].mean():.3f}

CORRELATION
Pearson r = {corr.statistic:.3f}
p-value = {corr.pvalue:.6f}
This describes linear association in synthetic data; it does not establish causation.

GROUP COMPARISON
Lower satisfaction (<=3): n={n2}, mean repeat intention={lower.mean():.3f}
Higher satisfaction (>=4): n={n1}, mean repeat intention={higher.mean():.3f}
Welch t={welch.statistic:.3f}, p={welch.pvalue:.6f}
Cohen's d (higher minus lower)={cohen_d:.3f}
Decision: {decision}.

INTERPRETATION CHECKLIST
- Statistical significance is not practical importance.
- Report effect size and group means, not only p-value.
- A non-significant result does not prove no relationship.
- Synthetic data cannot generalize to actual shoppers.
- Grouping ordinal scores loses information.
- Cross-sectional self-report data cannot establish causal influence.
"""
(OUT / "research_results_report.txt").write_text(report, encoding="utf-8")
print(report)
print(f"Outputs saved to: {OUT}")
