import pandas as pd
from src.transformations.format_converter import dataframe_to_avro
print(dataframe_to_avro(pd.DataFrame({"id":[1,2],"name":["A","B"]})))
