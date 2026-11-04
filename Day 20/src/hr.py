import random
from datetime import date, timedelta
from .common import fake, write_csv, rand_date, money

def generate(out, n_employees=1000):
    depts=["Engineering","Data","Finance","HR","Sales","Operations","Security"]
    departments=[dict(department_id=i+1, department_name=d) for i,d in enumerate(depts)]
    employees=[]
    for i in range(1,n_employees+1):
        hire=rand_date(date(2018,1,1),date(2026,1,1))
        employees.append(dict(employee_id=i, department_id=random.randint(1,len(depts)),
            first_name=fake.first_name(), last_name=fake.last_name(), email=f"employee{i}@example.test",
            job_title=random.choice(["Analyst","Engineer","Manager","Associate","Specialist"]),
            hire_date=hire, annual_salary=money(random.uniform(300000,2400000)), employment_status=random.choice(["active","active","active","leave"])))
    attendance=[]; payroll=[]
    for e in employees:
        for day_offset in range(0,30):
            d=date(2026,10,1)+timedelta(days=day_offset)
            if d.weekday()<5 and random.random()<0.92:
                attendance.append(dict(attendance_id=len(attendance)+1, employee_id=e["employee_id"],
                    attendance_date=d, status=random.choices(["present","absent","leave"],[90,5,5])[0]))
        gross=money(e["annual_salary"]/12)
        payroll.append(dict(payroll_id=len(payroll)+1,employee_id=e["employee_id"],
            pay_period="2026-10",gross_pay=gross, deductions=money(gross*random.uniform(.05,.18)),
            net_pay=money(gross*(1-random.uniform(.05,.18)))))
    write_csv(out/"hr_departments.csv",departments,list(departments[0]))
    write_csv(out/"hr_employees.csv",employees,list(employees[0]))
    write_csv(out/"hr_attendance.csv",attendance,list(attendance[0]))
    write_csv(out/"hr_payroll.csv",payroll,list(payroll[0]))
