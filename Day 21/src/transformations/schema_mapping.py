import pandas as pd

def standardize_customer_columns(df):
    mapping={"CustomerID":"customer_id","customerId":"customer_id",
             "CustomerName":"customer_name","name":"customer_name",
             "Email":"email","e_mail":"email","Region":"region"}
    out=df.rename(columns={c:mapping[c] for c in df.columns if c in mapping}).copy()
    if "customer_id" in out:
        out["customer_id"]=pd.to_numeric(out["customer_id"],errors="coerce").astype("Int64")
    return out

def add_source_metadata(df, source_name):
    out=df.copy()
    out["source_system"]=source_name
    out["ingested_at"]=pd.Timestamp.utcnow().isoformat()
    return out
