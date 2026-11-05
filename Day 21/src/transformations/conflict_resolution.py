import pandas as pd

def merge_customer_sources(frames):
    # Stable key: customer_id. Prefer the latest non-null value from later frames.
    valid=[f for f in frames if f is not None and not f.empty and "customer_id" in f]
    if not valid: return pd.DataFrame()
    merged=valid[0].copy()
    for frame in valid[1:]:
        merged=merged.merge(frame,on="customer_id",how="outer",suffixes=("","_new"))
        for col in list(merged.columns):
            if col.endswith("_new"):
                base=col[:-4]
                if base in merged:
                    merged[base]=merged[col].combine_first(merged[base])
                    merged.drop(columns=[col],inplace=True)
                else:
                    merged.rename(columns={col:base},inplace=True)
    return merged
