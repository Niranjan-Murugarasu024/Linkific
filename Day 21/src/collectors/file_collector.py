from pathlib import Path
import pandas as pd, json
from src.utils.logger import get_logger
log=get_logger("files")
RAW=Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)

def create_sample_files():
    customers=pd.DataFrame([
        {"customer_id":1,"customer_name":"Asha","email":"asha@example.com","region":"South"},
        {"customer_id":2,"customer_name":"Kiran","email":"kiran@example.com","region":"West"},
        {"customer_id":3,"customer_name":"Meera","email":"meera@example.com","region":"South"},
    ])
    sales=pd.DataFrame([
        {"order_id":1001,"customer_id":1,"product":"Keyboard","amount":1499.0},
        {"order_id":1002,"customer_id":2,"product":"Mouse","amount":799.0},
        {"order_id":1003,"customer_id":3,"product":"Monitor","amount":12999.0},
    ])
    customers.to_csv(RAW/"customers.csv",index=False)
    sales.to_excel(RAW/"sales.xlsx",index=False)
    (RAW/"inventory.json").write_text(json.dumps([
        {"sku":"KB-1","product":"Keyboard","stock":24},
        {"sku":"MS-1","product":"Mouse","stock":40},
        {"sku":"MN-1","product":"Monitor","stock":8}
    ],indent=2),encoding="utf-8")
    log.info("Created CSV, Excel and JSON samples")
    return customers,sales

def collect_files():
    create_sample_files()
    return {
      "customers":pd.read_csv(RAW/"customers.csv"),
      "sales":pd.read_excel(RAW/"sales.xlsx"),
      "inventory":pd.read_json(RAW/"inventory.json")
    }
