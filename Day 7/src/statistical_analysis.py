import pandas as pd
import numpy as np
from scipy import stats

def describe_numeric(df):
    """Expanded descriptive statistics for numeric columns."""
    numeric = df.select_dtypes(include=np.number)
    result = numeric.describe(percentiles=[.01, .05, .25, .5, .75, .95, .99]).T
    result["variance"] = numeric.var()
    result["skewness"] = numeric.skew()
    result["kurtosis_excess"] = numeric.kurt()
    return result

def pearson_test(df, x, y):
    """Pearson linear correlation and p-value using pairwise complete rows."""
    pair = df[[x, y]].dropna()
    r, p = stats.pearsonr(pair[x], pair[y])
    return {"x": x, "y": y, "n": len(pair), "pearson_r": r, "p_value": p}

def mann_whitney_test(group_a, group_b):
    """Non-parametric two-independent-group comparison."""
    a, b = pd.Series(group_a).dropna(), pd.Series(group_b).dropna()
    statistic, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    return {"n_a": len(a), "n_b": len(b), "u_statistic": statistic, "p_value": p}
