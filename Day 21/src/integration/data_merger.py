import pandas as pd

def merge_sales_customers(sales,customers):
    if sales.empty or customers.empty: return sales.copy()
    return sales.merge(customers,on="customer_id",how="left",validate="many_to_one")

def union_source_records(frames):
    cleaned=[f for f in frames if f is not None and not f.empty]
    return pd.concat(cleaned,ignore_index=True,sort=False) if cleaned else pd.DataFrame()
