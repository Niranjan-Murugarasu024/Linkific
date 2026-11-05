import pandas as pd

def clean_customers(df):
    out=df.copy()
    for col in ["customer_name","email","region"]:
        if col in out: out[col]=out[col].astype("string").str.strip()
    if "email" in out:
        out["email"]=out["email"].str.lower()
    if "customer_id" in out:
        out=out.dropna(subset=["customer_id"])
        out=out.drop_duplicates(subset=["customer_id"],keep="last")
    return out
