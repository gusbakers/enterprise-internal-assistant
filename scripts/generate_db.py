"""
CRESTLINE TECHNOLOGIES — DATABASE GENERATOR
Run: python scripts/generate_db.py
"""

import sqlite3
import random
import os
from datetime import date, timedelta

random.seed(42)
DB_PATH = "data/crestline.db"

def get_quarter(month):
    return f"Q{(month - 1) // 3 + 1}"

def random_date(start_year=2020, end_year=2024):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()

def create_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables(conn):
    conn.executescript("""
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS campaigns;
        DROP TABLE IF EXISTS metrics;

        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            quarter TEXT NOT NULL,
            units_sold INTEGER NOT NULL,
            revenue REAL NOT NULL,
            market TEXT NOT NULL
        );

        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            salary INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            location TEXT NOT NULL,
            employment_type TEXT NOT NULL
        );

        CREATE TABLE campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            campaign_name TEXT NOT NULL,
            budget REAL NOT NULL,
            channel TEXT NOT NULL,
            quarter TEXT NOT NULL,
            year INTEGER NOT NULL,
            impressions INTEGER NOT NULL,
            clicks INTEGER NOT NULL,
            conversions INTEGER NOT NULL,
            ctr REAL NOT NULL
        );

        CREATE TABLE metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            mrr REAL NOT NULL,
            churn_rate REAL NOT NULL,
            active_users INTEGER NOT NULL,
            new_customers INTEGER NOT NULL,
            nps_score REAL NOT NULL
        );
    """)
    conn.commit()
    print("✅ Tables created")

def seed_sales(conn):
    products = {
        "Crestline X":     {"price": 499,  "base_units": 8000,  "std_dev": 1200, "q4_boost": 1.35},
        "Crestline Pro":   {"price": 1999, "base_units": 3000,  "std_dev": 500,  "q4_boost": 1.20},
        "Crestline Watch": {"price": 299,  "base_units": 5000,  "std_dev": 900,  "q4_boost": 1.45},
        "Crestline OS":    {"price": 229,  "base_units": 10000, "std_dev": 2000, "q4_boost": 1.10},
        "Crestline Cloud": {"price": 65,   "base_units": 20000, "std_dev": 3000, "q4_boost": 1.05},
    }
    markets = ["USA", "Canada", "UK"]
    rows = []
    for month in range(1, 13):
        quarter = get_quarter(month)
        for product, cfg in products.items():
            boost = cfg["q4_boost"] if quarter == "Q4" else 1.0
            growth = 1 + (month - 1) * random.uniform(0.005, 0.02)
            units = max(500, int(random.gauss(cfg["base_units"] * growth * boost, cfg["std_dev"])))
            revenue = round(units * cfg["price"] * random.uniform(0.97, 1.03), 2)
            rows.append((product, month, 2024, quarter, units, revenue, random.choice(markets)))
    conn.executemany(
        "INSERT INTO sales (product, month, year, quarter, units_sold, revenue, market) VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"✅ Sales: {len(rows)} rows inserted")

def seed_employees(conn):
    departments = {
        "Engineering": {"count": 30, "roles": ["Software Engineer", "Senior Engineer", "Staff Engineer", "Engineering Manager"], "salary_range": (95000, 185000)},
        "Product":     {"count": 15, "roles": ["Product Manager", "Senior PM", "Product Designer", "UX Researcher"], "salary_range": (90000, 170000)},
        "Marketing":   {"count": 15, "roles": ["Marketing Manager", "Content Strategist", "Growth Analyst", "Brand Designer"], "salary_range": (75000, 140000)},
        "Sales":       {"count": 20, "roles": ["Account Executive", "Sales Manager", "SDR", "Enterprise AE"], "salary_range": (70000, 160000)},
        "HR":          {"count": 10, "roles": ["HR Manager", "Recruiter", "People Ops", "HR Business Partner"], "salary_range": (65000, 125000)},
        "Finance":     {"count": 10, "roles": ["Financial Analyst", "Controller", "FP&A Manager", "Accountant"], "salary_range": (80000, 150000)},
    }
    first_names = ["James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda","William","Barbara","David","Susan","Richard","Jessica","Thomas","Sarah","Charles","Karen","Sophia","Liam","Noah","Emma","Olivia","Ava","Lucas","Mason","Ethan","Priya","Diego","Carlos","Maria","Elena","Yuki","Jin","Alex","Jordan","Taylor","Morgan","Casey","Cameron"]
    last_names  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Martinez","Anderson","Taylor","Thomas","Hernandez","Moore","Jackson","Martin","Lee","Patel","Kim","Nguyen","Chen","Wang","Kumar","Singh","Rodriguez","Lewis","Robinson","Walker","White","Harris","Clark","Young","Allen","Wright","Scott","Torres","Hill","Flores","Green"]
    locations = ["New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA", "Remote"]
    employment_types = ["Full-time", "Full-time", "Full-time", "Contract"]
    used_emails = set()
    rows = []
    for dept, cfg in departments.items():
        for _ in range(cfg["count"]):
            first = random.choice(first_names)
            last  = random.choice(last_names)
            base  = f"{first.lower()}.{last.lower()}@crestline.com"
            email = base
            c = 2
            while email in used_emails:
                email = f"{first.lower()}.{last.lower()}{c}@crestline.com"
                c += 1
            used_emails.add(email)
            rows.append((
                f"{first} {last}", email,
                random.choice(cfg["roles"]), dept,
                random.randint(*cfg["salary_range"]),
                random_date(), random.choice(locations),
                random.choice(employment_types),
            ))
    conn.executemany(
        "INSERT INTO employees (name, email, role, department, salary, start_date, location, employment_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"✅ Employees: {len(rows)} rows inserted")

def seed_campaigns(conn):
    campaign_map = {
        "Crestline X":     ["Power Meets Simplicity", "X Marks the Future", "Unleash X", "X — Everyday Extraordinary"],
        "Crestline Pro":   ["Work Without Limits", "Pro for Professionals", "Enterprise-Grade. Consumer-Simple.", "Pro — Built for You"],
        "Crestline Watch": ["Time Redefined", "Health First", "Always On", "Your Health. Your Time."],
        "Crestline OS":    ["OS Built for Business", "Your OS Evolved", "Seamless by Design", "Work Flows Here"],
        "Crestline Cloud": ["Secure. Scale. Succeed.", "Cloud Without Compromise", "Business in the Cloud", "Your Data, Everywhere"],
    }
    channels  = ["Instagram", "LinkedIn", "YouTube", "Google Ads", "Email", "Events"]
    quarters  = ["Q1", "Q2", "Q3", "Q4"]
    rows = []
    for product, names in campaign_map.items():
        for i, quarter in enumerate(quarters):
            impressions = random.randint(400000, 5000000)
            ctr_pct     = random.uniform(0.018, 0.085)
            clicks      = int(impressions * ctr_pct)
            conversions = int(clicks * random.uniform(0.04, 0.14))
            rows.append((
                product, names[i % len(names)],
                round(random.uniform(150000, 2500000), 2),
                random.choice(channels), quarter, 2024,
                impressions, clicks, conversions, round(ctr_pct * 100, 2),
            ))
    conn.executemany(
        "INSERT INTO campaigns (product, campaign_name, budget, channel, quarter, year, impressions, clicks, conversions, ctr) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"✅ Campaigns: {len(rows)} rows inserted")

def seed_metrics(conn):
    mrr = 2400000
    active_users = 45000
    rows = []
    for month in range(1, 13):
        mrr = int(mrr * random.uniform(1.02, 1.06))
        active_users = int(active_users * random.uniform(1.02, 1.05))
        rows.append((
            month, 2024, mrr,
            round(random.uniform(1.6, 3.4), 2),
            active_users,
            random.randint(700, 2100),
            round(random.uniform(44, 71), 1),
        ))
    conn.executemany(
        "INSERT INTO metrics (month, year, mrr, churn_rate, active_users, new_customers, nps_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"✅ Metrics: {len(rows)} rows inserted")

def verify(conn):
    print("\n📊 Verification:")
    for table in ["sales", "employees", "campaigns", "metrics"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"   {table:<12} → {count} rows")

def main():
    print("🚀 Crestline Data Engineer — Generating SQLite Database")
    print("=" * 55)
    conn = create_connection()
    create_tables(conn)
    seed_sales(conn)
    seed_employees(conn)
    seed_campaigns(conn)
    seed_metrics(conn)
    verify(conn)
    conn.close()
    print("=" * 55)
    print(f"✅ Database ready → {DB_PATH}")

if __name__ == "__main__":
    main()
    