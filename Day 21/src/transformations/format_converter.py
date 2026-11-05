from pathlib import Path
import json, pandas as pd
from lxml import etree
from src.utils.logger import get_logger
log=get_logger("formats")
OUT=Path("data/processed"); OUT.mkdir(parents=True,exist_ok=True)

def json_to_dataframe(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    df=pd.json_normalize(data)
    df.to_csv(OUT/"json_to_dataframe.csv",index=False)
    return df

def parse_xml(xml_text):
    root=etree.fromstring(xml_text.encode("utf-8"))
    return [{"tag":child.tag,"text":child.text} for child in root]

def dataframe_to_parquet(df,path="data/processed/data.parquet"):
    df.to_parquet(path,index=False)
    return path

def dataframe_to_avro(df,path="data/processed/data.avro"):
    from fastavro import writer, parse_schema
    schema=parse_schema({"type":"record","name":"Record","fields":[
      {"name":"record_json","type":"string"}]})
    records=[{"record_json":row.to_json()} for _,row in df.iterrows()]
    with open(path,"wb") as f: writer(f,schema,records)
    return path

def convert_examples():
    xml=parse_xml("<catalog><item>Keyboard</item><item>Mouse</item></catalog>")
    sample=pd.DataFrame({"id":[1,2],"value":["alpha","beta"]})
    parquet=dataframe_to_parquet(sample)
    avro=dataframe_to_avro(sample)
    return {"xml":xml,"parquet":parquet,"avro":avro}
