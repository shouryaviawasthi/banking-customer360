# 🏦 Banking Customer 360 & Data Quality

> A production-grade, end-to-end banking analytics platform built on **PostgreSQL**, **Python**, and **Streamlit** — covering data generation, ETL/data quality, SQL analytics, and an interactive dashboard.

---

## 📌 What Is This Project?

This project simulates a real-world **retail banking data platform** — the kind used by banks to understand their customers, monitor account health, and track financial transactions.

The core idea is called **Customer 360**: instead of looking at a customer's profile, accounts, and transactions in separate places, we combine everything into **one unified view per customer** so that analysts and business teams can answer questions like:

- Who are our most active customers?
- Which cities have the most inactive customers?
- How much credit vs debit happened this month?
- Which accounts have zero transactions?
- What is our overall data quality score?

---

## 🗂️ Project Structure

```
banking-customer-360/
│
├── data/
│   ├── raw/                        # Synthetic CSV files with intentional errors
│   │   ├── customers.csv           # 1,005 rows (5 duplicates, missing emails/phones)
│   │   ├── accounts.csv            # 1,500 rows
│   │   └── transactions.csv        # 10,000 rows (negatives, bad status values)
│   │
│   └── processed/                  # ETL-cleaned output (Phase 2)
│       ├── customers_clean.csv
│       ├── accounts_clean.csv
│       ├── transactions_clean.csv
│       ├── data_quality_report.csv
│       ├── data_quality_report.txt
│       └── rejected_records/
│
├── database/
│   ├── schema.sql                  # PostgreSQL DDL — tables, constraints, indexes
│   └── seed.sql                    # Auto-generated INSERT statements (clean data)
│
├── scripts/
│   ├── generate_data.py            # Synthetic data generator (Phase 1)
│   ├── etl_pipeline.py             # Data quality ETL pipeline (Phase 2)
│   └── verify_phase1.py            # Validation checks (Phase 1)
│
├── sql/
│   ├── customer_360.sql            # PostgreSQL VIEW: vw_customer_360 (Phase 3)
│   ├── customer_analytics.sql      # Customer-level SQL queries (Phase 3)
│   ├── account_analytics.sql       # Account-level SQL queries (Phase 3)
│   ├── transaction_analytics.sql   # Transaction-level SQL queries (Phase 3)
│   └── kpi_queries.sql             # PostgreSQL VIEW: vw_kpi_dashboard (Phase 3)
│
├── config/
│   └── .env.example                # Database credentials template
│
├── dashboard.py                    # Streamlit + Plotly dashboard (Phase 4)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|:---|:---|:---|
| Data Generation | Python 3.12, pandas | Synthetic Indian banking data |
| Database | PostgreSQL 16 | Core relational store |
| ETL / Data Quality | Python 3.12, pandas | Cleaning, validation, profiling |
| SQL Analytics | PostgreSQL SQL | Views, CTEs, window functions |
| Dashboard | Streamlit 1.65 | Interactive multi-page web app |
| Visualizations | Plotly Express / Graph Objects | Charts and graphs |
| DB Driver | pg8000 (pure Python) | Connects Python to PostgreSQL |
| Config | python-dotenv | Reads .env credentials |

---

## 🔄 How Everything Works — Data Flow

`
Step 1: Generate Synthetic Data
      scripts/generate_data.py
             ↓
      data/raw/ (CSV files with errors)
             ↓
Step 2: ETL Pipeline (Data Quality)
      scripts/etl_pipeline.py
             ↓
      data/processed/ (clean CSVs + reports)
             ↓
Step 3: Seed PostgreSQL 16
      database/schema.sql  →  Creates tables + indexes
      database/seed.sql    →  Inserts 1,000 customers, 1,500 accounts, 10,000 transactions
             ↓
Step 4: SQL Analytical Layer
      sql/customer_360.sql    →  Creates vw_customer_360 VIEW
      sql/kpi_queries.sql     →  Creates vw_kpi_dashboard VIEW
             ↓
Step 5: Streamlit Dashboard
      dashboard.py  →  Reads from PostgreSQL views  →  Renders charts
`

---

## 📦 Phase-by-Phase Breakdown

### Phase 1 — Banking Data + PostgreSQL Setup

**Goal:** Design a normalized PostgreSQL database and generate realistic synthetic Indian banking data.

**Database Design:**

`
customers (1) ──→ accounts (N) ──→ transactions (N)
  customer_id        account_id        transaction_id
  first_name         customer_id (FK)  account_id (FK)
  last_name          account_type      transaction_date
  date_of_birth      account_status    transaction_type
  gender             balance           amount
  email              opening_date      transaction_status
  phone              branch_code       channel
  city, state
  customer_status
  customer_since
`

**Data constraints enforced in PostgreSQL:**
- customer_status must be ACTIVE or INACTIVE
- account_type must be SAVINGS, CURRENT, or SALARY
- account_status must be ACTIVE, INACTIVE, or CLOSED
- balance >= 0
- amount > 0
- transaction_status must be SUCCESS, FAILED, or PENDING
- channel must be ATM, ONLINE, MOBILE, BRANCH, or UPI

**Performance indexes:**
- idx_accounts_customer_id — speeds up customer → accounts JOINs
- idx_transactions_account_id — speeds up account → transactions JOINs
- idx_transactions_date — speeds up date-range queries and monthly reports
- idx_transactions_type — speeds up CREDIT vs DEBIT filtering

**Intentional data quality issues in raw CSVs:**

| Issue | Count |
|:---|:---|
| Missing email addresses | 25 records |
| Missing phone numbers | 20 records |
| Duplicate customer rows | 5 rows |
| Inconsistent city names (Bangalore, mumbai, New Delhi) | ~35 records |
| Negative transaction amounts | 10 records |
| Non-standard transaction status (COMPLETED) | 10 records |

---

### Phase 2 — Python/Pandas ETL + Data Quality

**Goal:** Read raw CSV data, detect quality issues, clean the data, and produce reports.

**ETL Steps:**

| Step | What happens |
|:---|:---|
| Load raw CSVs | Read data/raw/*.csv into pandas DataFrames |
| Detect duplicates | Find duplicate customer_id rows |
| Detect missing values | Find NULL email and phone |
| Remove bad records | Send them to data/processed/rejected_records/ |
| Fix city names | Strip spaces, title-case, replace Bangalore → Bengaluru |
| Remove negative amounts | Filter out transactions where amount <= 0 |
| Standardize statuses | Replace COMPLETED → SUCCESS |
| Save clean data | Write *_clean.csv files |
| Generate report | Write data_quality_report.csv and .txt |

**Data Quality Summary:**

| Entity | Raw Records | Valid | Rejected |
|:---|:---|:---|:---|
| Customers | 1,005 | 965 | 40 |
| Accounts | 1,500 | 1,500 | 0 |
| Transactions | 10,000 | 9,990 | 10 |

---

### Phase 3 — Customer 360 + SQL Analytics + KPI Layer

**Goal:** Build an analytical SQL layer on top of the clean PostgreSQL data.

#### vw_customer_360 — Core Customer 360 View

One row per customer combining profile + accounts + transactions.

**Why CTEs are critical — Preventing Double Counting:**

Because customers → accounts → transactions is 1-to-many-to-many, a naive JOIN inflates totals for customers with multiple accounts. We solve this by pre-aggregating accounts and transactions separately in CTEs before the final JOIN.

`sql
WITH customer_accounts AS (
    SELECT customer_id, COUNT(*), SUM(balance), AVG(balance)
    FROM accounts GROUP BY customer_id
),
customer_transactions AS (
    SELECT a.customer_id, COUNT(t.*), SUM(credit), SUM(debit)
    FROM accounts a LEFT JOIN transactions t ON a.account_id = t.account_id
    GROUP BY a.customer_id
)
SELECT c.*, ca.*, ct.*
FROM customers c
LEFT JOIN customer_accounts ca ON c.customer_id = ca.customer_id
LEFT JOIN customer_transactions ct ON c.customer_id = ct.customer_id
`

**Customer Activity Business Rule:**
A customer is ACTIVE if they have at least one SUCCESSFUL transaction in the last 90 days. Otherwise INACTIVE.
Note: This is different from customer_status (set at registration). Activity status is calculated live from transaction behavior.

**Advanced SQL Concepts Used:**

| Concept | Where used |
|:---|:---|
| CTE | vw_customer_360 — pre-aggregation |
| Window Function RANK() | customer_analytics.sql — top customers by balance |
| CASE WHEN | Credit/debit split, activity status |
| LEFT JOIN | Includes customers with zero transactions |
| GROUP BY + HAVING | Multi-account customers |
| TO_CHAR() | Monthly trend grouping |
| INTERVAL '90 days' | Activity status window |
| PostgreSQL VIEW | vw_customer_360 and vw_kpi_dashboard |

---

### Phase 4 — Streamlit + Plotly KPI Dashboard

**Goal:** Interactive multi-page web dashboard connecting live to PostgreSQL via pg8000.

**Run:**
`powershell
.\venv\Scripts\streamlit run dashboard.py
`

---

## 📊 Dashboard — Page by Page & Chart by Chart

### Page 1: 📊 Overview

The main landing page — a full snapshot of the entire banking system.

**KPI Cards — Row 1 (Customer Metrics):**
| Card | What it shows |
|:---|:---|
| Total Customers | All customers in the system (1,000) |
| Active Customers | Had a successful transaction in the last 90 days + % |
| Inactive Customers | No recent transaction activity + % |
| Total Balance (₹) | Sum of all account balances |

**KPI Cards — Row 2 (Account & Transaction Metrics):**
| Card | What it shows |
|:---|:---|
| Total Accounts | All bank accounts opened (1,500) |
| Total Transactions | All transactions ever recorded (10,000) |
| Successful Transactions | Count + success rate % |
| Avg Transaction (₹) | Average value of a successful transaction |

**Chart 1 — Active vs Inactive Customers (Donut Pie):**
Percentage split between active (green) and inactive (red) customers. Instantly shows if the customer base is engaged.

**Chart 2 — Account Status Breakdown (Bar Chart):**
Count of Active (blue), Inactive (yellow), and Closed (red) accounts. Monitors account portfolio health.

**Chart 3 — Monthly Credit vs Debit Trend (Filled Area Line):**
Month-by-month volume of money flowing IN (credit, blue) vs OUT (debit, red). Spots seasonal patterns or anomalies.

---

### Page 2: 👥 Customers

Deep-dive with a filter dropdown (All / ACTIVE / INACTIVE).

**Chart 1 — Top 10 Cities by Customer Count (Horizontal Bar with Color Scale):**
Which cities have the most customers. Darker color = more active customers in that city.

**Chart 2 — Customers by Account Count (Bar):**
How many customers have 1, 2, or 3+ accounts. Shows multi-banking behavior.

**Table — Top 20 Customers by Total Balance:**
Ranked list with Customer ID, Name, City, State, Accounts, Balance (₹), Transactions, and a 🟢/🔴 activity badge.

---

### Page 3: 🏧 Accounts

**KPIs:** Total / Active / Inactive / Closed account counts.

**Chart 1 — Balance by Account Type (Bar):**
Total money held in SAVINGS (blue) vs CURRENT (yellow) vs SALARY (green) accounts.

**Chart 2 — Account Distribution by Type (Donut):**
Percentage share of each account type in the portfolio.

**Table — Average Balance by Account Type:**
How much customers hold on average per account type.

---

### Page 4: 💳 Transactions

**KPIs Row 1:** Total / Successful / Failed / Pending transaction counts.
**KPIs Row 2:** Total Credit (₹) / Total Debit (₹) / Average Transaction (₹).

**Chart 1 — Transactions by Channel (Bar with Color Scale):**
Count of transactions per channel — ATM, ONLINE, MOBILE, BRANCH, UPI. Darker = higher ₹ volume.

**Chart 2 — Transaction Status Split (Donut):**
Percentage of SUCCESS (green) / FAILED (red) / PENDING (yellow) transactions.

**Chart 3 — Monthly Transaction Volume (Area Chart):**
Total successful ₹ value per month. Spots busy periods (salary months) and quiet months.

---

### Page 5: 🔍 Data Quality

Surfaces Phase 2 ETL results.

**KPIs:** Total raw records / Valid kept / Rejected removed / Overall DQ Score %.

**Table — Breakdown by Entity:**
| Entity | Raw | Valid | Rejected | DQ Score | Issues |
|:---|:---|:---|:---|:---|:---|
| Customers | 1,005 | 965 | 40 | 96.0% | 5 duplicates, 25 missing emails, 20 missing phones |
| Accounts | 1,500 | 1,500 | 0 | 100.0% | None |
| Transactions | 10,000 | 9,990 | 10 | 99.9% | 10 negative amounts |

**Chart — Valid vs Rejected (Grouped Bar):**
Side-by-side green (valid) and red (rejected) bars per entity. Immediately shows which entity had the most issues.

---

## 🚀 How to Run the Project

### Prerequisites
- Python 3.12+
- PostgreSQL 16 locally installed

### Commands

`powershell
# 1. Activate environment
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate synthetic data
python scripts/generate_data.py

# 4. Add PostgreSQL to PATH
C:/Users/shour/.gemini/antigravity-ide/bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Docker\Docker\resources\bin;C:\Program Files\nodejs\;C:\Program Files\Git\cmd;C:\Users\shour\AppData\Local\Programs\Python\Python312\Scripts\;C:\Users\shour\AppData\Local\Programs\Python\Python312\;C:\Users\shour\AppData\Local\Programs\Python\Python314\Scripts\;C:\Users\shour\AppData\Local\Programs\Python\Python314\;C:\Users\shour\AppData\Local\Microsoft\WindowsApps;C:\Users\shour\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\shour\AppData\Local\Programs\Antigravity\bin;C:\Users\shour\AppData\Roaming\npm;C:\Users\shour\AppData\Local\Programs\Antigravity IDE\bin;C:\Users\shour\AppData\Local\Python\bin;C:\Users\shour\Downloads\sqlite-tools-win-x64-3530300; += ";C:\Program Files\PostgreSQL\16\bin"
="your_password"

# 5. Create and seed the database
createdb.exe -U postgres banking_customer360
psql.exe -U postgres -d banking_customer360 -f database/schema.sql
psql.exe -U postgres -d banking_customer360 -f database/seed.sql

# 6. Create SQL views (Phase 3)
psql.exe -U postgres -d banking_customer360 -f sql/customer_360.sql
psql.exe -U postgres -d banking_customer360 -f sql/kpi_queries.sql

# 7. Run ETL pipeline (Phase 2)
python scripts/etl_pipeline.py

# 8. Launch dashboard
.\venv\Scripts\streamlit run dashboard.py
# Open: http://localhost:8501
`

---

## 📋 Phase Completion Status

| Phase | Status | Description |
|:---|:---:|:---|
| Phase 1: Banking Data + PostgreSQL | ✅ Complete | Schema, synthetic data, seed script |
| Phase 2: ETL + Data Quality | ✅ Complete | ETL pipeline, validation, cleaning, reports |
| Phase 3: Customer 360 + SQL Analytics | ✅ Complete | Views, KPIs, analytical queries |
| Phase 4: Streamlit Dashboard | ✅ Complete | Multi-page interactive dashboard |
