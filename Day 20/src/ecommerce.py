from datetime import date, timedelta
import random
from faker import Faker
from .common import fake, write_csv, rand_date, money

def generate(out, n_orders=100000, n_customers=None, n_products=500):
    n_customers = n_customers or max(1000, n_orders // 10)
    customers=[]
    for i in range(1,n_customers+1):
        customers.append(dict(customer_id=i, first_name=fake.first_name(), last_name=fake.last_name(),
            email=f"customer{i}@example.test", phone=fake.phone_number(),
            city=fake.city(), country=fake.country(), created_at=rand_date(date(2020,1,1),date(2026,1,1))))
    products=[]
    categories=["Electronics","Home","Books","Clothing","Sports","Beauty","Toys"]
    for i in range(1,n_products+1):
        products.append(dict(product_id=i, product_name=f"{fake.word().title()} {fake.word().title()}",
            category=random.choice(categories), unit_price=money(random.uniform(5,1500)), stock=random.randint(0,5000)))
    orders=[]; items=[]; payments=[]
    for oid in range(1,n_orders+1):
        cid=random.randint(1,n_customers); od=rand_date(date(2023,1,1),date(2026,10,31))
        status=random.choices(["completed","processing","cancelled","returned"],[70,15,10,5])[0]
        chosen=random.sample(range(1,n_products+1),random.randint(1,4))
        total=0.0
        for ix,pid in enumerate(chosen,1):
            qty=random.randint(1,5); price=products[pid-1]["unit_price"]
            line=money(qty*price); total+=line
            items.append(dict(order_item_id=len(items)+1, order_id=oid, product_id=pid,
                quantity=qty, unit_price=price, line_total=line))
        total=money(total)
        orders.append(dict(order_id=oid, customer_id=cid, order_date=od, status=status, total_amount=total))
        if status!="cancelled":
            payments.append(dict(payment_id=len(payments)+1, order_id=oid, payment_date=od+timedelta(days=random.randint(0,3)),
                method=random.choice(["card","upi","netbanking","wallet"]), amount=total,
                payment_status="refunded" if status=="returned" else "paid"))
    write_csv(out/"ecommerce_customers.csv",customers,list(customers[0]))
    write_csv(out/"ecommerce_products.csv",products,list(products[0]))
    write_csv(out/"ecommerce_orders.csv",orders,list(orders[0]))
    write_csv(out/"ecommerce_order_items.csv",items,list(items[0]))
    write_csv(out/"ecommerce_payments.csv",payments,list(payments[0]))
