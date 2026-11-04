import argparse
from pathlib import Path
from .common import seed_all, ensure_dir
from .ecommerce import generate as gen_ecommerce
from .hr import generate as gen_hr
from .finance import generate as gen_finance

def main():
    p=argparse.ArgumentParser(description="Generate three relational synthetic databases.")
    p.add_argument("--orders",type=int,default=100000)
    p.add_argument("--employees",type=int,default=1000)
    p.add_argument("--financial-transactions",type=int,default=100000)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--out",default="data/generated")
    a=p.parse_args()
    out=Path(a.out); ensure_dir(out); seed_all(a.seed)
    print("Generating e-commerce...")
    gen_ecommerce(out,a.orders)
    print("Generating HR...")
    gen_hr(out,a.employees)
    print("Generating finance...")
    gen_finance(out,a.financial_transactions)
    print(f"Done. CSV files: {out.resolve()}")
if __name__=="__main__": main()
