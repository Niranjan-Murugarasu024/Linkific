import pandas as pd
from src.transformations.format_converter import dataframe_to_parquet
print(dataframe_to_parquet(pd.DataFrame({"id":[1,2],"name":["A","B"]})))
