import csv
from pathlib import Path
def rows(name):
    with (Path("data/generated")/name).open(encoding="utf-8",newline="") as f: return list(csv.DictReader(f))
def main():
    customers=rows("ecommerce_customers.csv"); products=rows("ecommerce_products.csv")
    orders=rows("ecommerce_orders.csv"); items=rows("ecommerce_order_items.csv"); payments=rows("ecommerce_payments.csv")
    cids={r["customer_id"] for r in customers}; pids={r["product_id"] for r in products}; oids={r["order_id"] for r in orders}
    assert len(cids)==len(customers),"Duplicate ecommerce customer IDs"
    assert len(pids)==len(products),"Duplicate product IDs"
    assert len(oids)==len(orders),"Duplicate order IDs"
    assert all(r["customer_id"] in cids for r in orders),"Order customer FK failure"
    assert all(r["order_id"] in oids and r["product_id"] in pids for r in items),"Order item FK failure"
    assert all(int(r["quantity"])>0 and float(r["line_total"])>=0 for r in items),"Invalid order item"
    assert all(r["order_id"] in oids and float(r["amount"])>=0 for r in payments),"Payment FK/amount failure"
    print(f"PASS e-commerce: {len(customers):,} customers, {len(products):,} products, {len(orders):,} orders, {len(items):,} items, {len(payments):,} payments")
    # HR / finance FK checks
    emp=rows("hr_employees.csv"); dept={r["department_id"] for r in rows("hr_departments.csv")}; eids={r["employee_id"] for r in emp}
    assert all(r["department_id"] in dept for r in emp)
    assert all(r["employee_id"] in eids for r in rows("hr_attendance.csv")+rows("hr_payroll.csv"))
    faccts=rows("finance_accounts.csv"); aids={r["account_id"] for r in faccts}; fcids={r["fin_customer_id"] for r in rows("finance_customers.csv")}
    assert all(r["fin_customer_id"] in fcids for r in faccts)
    assert all(r["account_id"] in aids and float(r["amount"])>=0 for r in rows("finance_transactions.csv"))
    print("PASS HR and finance foreign keys and amount constraints")
if __name__=="__main__": main()
