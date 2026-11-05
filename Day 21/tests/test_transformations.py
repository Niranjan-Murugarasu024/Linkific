import pandas as pd
from src.transformations.data_cleaning import clean_customers
from src.transformations.schema_mapping import standardize_customer_columns

def test_schema_mapping():
    out=standardize_customer_columns(pd.DataFrame({"CustomerID":[1],"CustomerName":["A"]}))
    assert "customer_id" in out and "customer_name" in out

def test_cleaning_deduplicates():
    df=pd.DataFrame({"customer_id":[1,1],"email":["A@X.COM","a@x.com"]})
    out=clean_customers(df)
    assert len(out)==1
    assert out.iloc[0]["email"]=="a@x.com"
