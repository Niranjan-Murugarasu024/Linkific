import random
from datetime import date
from .common import fake, write_csv, rand_date, money

def generate(out, n_transactions=100000, n_customers=None, n_accounts=None):
    n_customers=n_customers or max(1000,n_transactions//20)
    n_accounts=n_accounts or max(n_customers, n_customers*2)
    customers=[dict(fin_customer_id=i,full_name=fake.name(),email=f"fin{i}@example.test",
        country=fake.country(),created_date=rand_date(date(2019,1,1),date(2026,1,1))) for i in range(1,n_customers+1)]
    accounts=[]
    for i in range(1,n_accounts+1):
        accounts.append(dict(account_id=i,fin_customer_id=random.randint(1,n_customers),
            account_type=random.choice(["checking","savings","credit"]),currency=random.choice(["INR","USD","EUR"]),
            opening_balance=money(random.uniform(1000,500000))))
    transactions=[]
    for i in range(1,n_transactions+1):
        a=random.choice(accounts); typ=random.choice(["credit","debit"])
        amount=money(random.lognormvariate(7,1.1))
        transactions.append(dict(transaction_id=i,account_id=a["account_id"],transaction_date=rand_date(date(2023,1,1),date(2026,10,31)),
            transaction_type=typ,amount=amount,merchant=fake.company(),description=fake.sentence(nb_words=5),
            channel=random.choice(["card","upi","bank_transfer","atm","online"]),status=random.choices(["posted","pending","reversed"],[90,7,3])[0]))
    write_csv(out/"finance_customers.csv",customers,list(customers[0]))
    write_csv(out/"finance_accounts.csv",accounts,list(accounts[0]))
    write_csv(out/"finance_transactions.csv",transactions,list(transactions[0]))
