"""
Banking Customer 360 & Data Quality - Data Generation Script (Phase 1)
-----------------------------------------------------------------------
This script generates synthetic banking data for 1,000 customers, ~1,500 accounts,
and ~10,000 transactions with realistic Indian banking context.

It outputs:
1. RAW datasets with controlled data-quality issues in `data/raw/`:
   - customers.csv
   - accounts.csv
   - transactions.csv
2. CLEAN PostgreSQL seed SQL file in `database/seed.sql` for initial database loading.

Reproducibility:
Set SEED = 42 for fixed random generation.
"""

import os
import random
import datetime
import pandas as pd

# Set fixed random seed for reproducibility
SEED = 42
random.seed(SEED)

# Define directories relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
DATABASE_DIR = os.path.join(BASE_DIR, "database")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# CONSTANTS & SAMPLE LOOKUPS (INDIAN BANKING CONTEXT)
# -----------------------------------------------------------------------------
MALE_NAMES = [
    "Aarav", "Vihaan", "Vivaan", "Aditya", "Sai", "Arjun", "Reyansh", "Ganesh",
    "Rajesh", "Suresh", "Amit", "Vikram", "Rohan", "Sanjay", "Rahul", "Vijay",
    "Pravin", "Deepak", "Sunil", "Manish", "Alok", "Karan", "Nitin", "Prashant"
]

FEMALE_NAMES = [
    "Aadhya", "Diya", "Ananya", "Priya", "Ishani", "Kavya", "Sneha", "Pooja",
    "Meera", "Sunita", "Anita", "Ritu", "Deepika", "Neha", "Swati", "Shruti",
    "Lakshmi", "Preeti", "Aarti", "Divya", "Shalini", "Radhika", "Bhavna"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Iyer", "Singh", "Kumar", "Gupta", "Joshi",
    "Mehta", "Rao", "Nair", "Chatterjee", "Das", "Mukherjee", "Reddy",
    "Kulkarni", "Deshmukh", "Bhatt", "Chowdhury", "Aggarwal", "Pillai", "Shah"
]

LOCATIONS = [
    ("Mumbai", "Maharashtra", "400001"),
    ("Delhi", "Delhi", "110001"),
    ("Bengaluru", "Karnataka", "560001"),
    ("Hyderabad", "Telangana", "500001"),
    ("Chennai", "Tamil Nadu", "600001"),
    ("Kolkata", "West Bengal", "700001"),
    ("Pune", "Maharashtra", "411001"),
    ("Ahmedabad", "Gujarat", "380001"),
    ("Jaipur", "Rajasthan", "302001"),
    ("Lucknow", "Uttar Pradesh", "226001"),
    ("Chandigarh", "Punjab", "160017"),
    ("Kochi", "Kerala", "682001")
]

BRANCH_CODES = ["BR001", "BR002", "BR003", "BR004", "BR005", "BR006", "BR007", "BR008"]

EMAIL_DOMAINS = ["gmail.com", "yahoo.co.in", "outlook.com", "rediffmail.com", "icloud.com"]

CREDIT_DESCRIPTIONS = [
    "Salary Credit", "UPI Transfer Received", "Dividend Credit",
    "FD Interest Credit", "Cash Deposit at Branch", "NEFT Inward Transfer", "IMPS Deposit"
]

DEBIT_DESCRIPTIONS = [
    "ATM Cash Withdrawal", "UPI Transfer to Merchant", "Utility Bill Payment",
    "Online Shopping - E-Commerce", "Credit Card Bill Pay", "POS Card Swipe - Groceries",
    "IMPS Outward Transfer", "DTH Mobile Recharge", "Fuel Station Payment"
]


# Helper to generate random date between start and end
def random_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    if days_between <= 0:
        return start_date
    random_days = random.randint(0, days_between)
    return start_date + datetime.timedelta(days=random_days)


# -----------------------------------------------------------------------------
# STEP 1: GENERATE CUSTOMERS DATA (1,000 Clean Customers)
# -----------------------------------------------------------------------------
print("Generating 1,000 synthetic banking customers...")

customers = []
start_dob = datetime.date(1950, 1, 1)
end_dob = datetime.date(2004, 12, 31)

start_since = datetime.date(2015, 1, 1)
end_since = datetime.date(2024, 1, 1)

for i in range(1, 1001):
    customer_id = f"CUST{i:05d}"
    gender = random.choice(["MALE", "FEMALE"])
    first_name = random.choice(MALE_NAMES) if gender == "MALE" else random.choice(FEMALE_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    dob = random_date(start_dob, end_dob).strftime("%Y-%m-%d")
    email = f"{first_name.lower()}.{last_name.lower()}{i}@randommail.com"
    
    # Realistic Indian mobile number format: +91 98XXXXXXXX / 97XXXXXXXX
    prefix = random.choice(["98", "97", "96", "99", "94", "93", "88", "70"])
    phone = f"+91 {prefix}{random.randint(1000000, 9999999)}"
    
    city, state, postal_code = random.choice(LOCATIONS)
    customer_since = random_date(start_since, end_since).strftime("%Y-%m-%d")
    
    # 92% Active, 8% Inactive
    customer_status = random.choices(["ACTIVE", "INACTIVE"], weights=[92, 8])[0]
    created_at = f"{customer_since} 09:00:00"

    customers.append({
        "customer_id": customer_id,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": dob,
        "gender": gender,
        "email": email,
        "phone": phone,
        "city": city,
        "state": state,
        "postal_code": postal_code,
        "customer_since": customer_since,
        "customer_status": customer_status,
        "created_at": created_at
    })

df_clean_customers = pd.DataFrame(customers)

# Create RAW customers dataframe with controlled data quality issues for Phase 2
df_raw_customers = df_clean_customers.copy()

# Issue 1: Missing emails (~25 records)
missing_email_idx = random.sample(range(1000), 25)
df_raw_customers.loc[missing_email_idx, "email"] = None

# Issue 2: Missing phones (~20 records)
missing_phone_idx = random.sample(range(1000), 20)
df_raw_customers.loc[missing_phone_idx, "phone"] = None

# Issue 3: Inconsistent City formatting (~35 records)
city_variations = {
    "Bengaluru": "Bangalore",
    "Mumbai": "mumbai ",
    "Delhi": " New Delhi",
    "Hyderabad": "hyderabad"
}
city_indices = df_raw_customers[df_raw_customers["city"].isin(city_variations.keys())].index
sample_city_indices = random.sample(list(city_indices), min(35, len(city_indices)))
for idx in sample_city_indices:
    original_city = df_raw_customers.loc[idx, "city"]
    df_raw_customers.loc[idx, "city"] = city_variations.get(original_city, original_city)

# Issue 4: Duplicate Customer Records (~5 duplicate rows appended at the end)
duplicates = df_raw_customers.iloc[random.sample(range(1000), 5)].copy()
df_raw_customers = pd.concat([df_raw_customers, duplicates], ignore_index=True)


# -----------------------------------------------------------------------------
# STEP 2: GENERATE ACCOUNTS DATA (~1,500 Accounts)
# -----------------------------------------------------------------------------
print("Generating 1,500 synthetic banking accounts...")

accounts = []
# Ensure each of the 1000 customers has at least 1 account
cust_ids = [c["customer_id"] for c in customers]
cust_since_map = {c["customer_id"]: c["customer_since"] for c in customers}

# First 1000 accounts for 1000 customers
assigned_cust_ids = cust_ids.copy()
# Remaining 500 accounts assigned randomly to existing customers (multi-account customers)
assigned_cust_ids.extend([random.choice(cust_ids) for _ in range(500)])
random.shuffle(assigned_cust_ids)

end_opening = datetime.date(2024, 6, 1)

for idx, cid in enumerate(assigned_cust_ids, start=1):
    account_id = f"ACC{idx:05d}"
    account_type = random.choices(["SAVINGS", "CURRENT", "SALARY"], weights=[60, 25, 15])[0]
    account_status = random.choices(["ACTIVE", "INACTIVE", "CLOSED"], weights=[85, 10, 5])[0]
    
    cust_since_dt = datetime.datetime.strptime(cust_since_map[cid], "%Y-%m-%d").date()
    opening_date = random_date(cust_since_dt, end_opening).strftime("%Y-%m-%d")
    
    # Realistic INR Balance
    if account_type == "SAVINGS":
        balance = round(random.uniform(2500.0, 500000.0), 2)
    elif account_type == "CURRENT":
        balance = round(random.uniform(25000.0, 1500000.0), 2)
    else: # SALARY
        balance = round(random.uniform(5000.0, 350000.0), 2)
        
    branch_code = random.choice(BRANCH_CODES)
    created_at = f"{opening_date} 10:00:00"

    accounts.append({
        "account_id": account_id,
        "customer_id": cid,
        "account_type": account_type,
        "account_status": account_status,
        "opening_date": opening_date,
        "balance": balance,
        "branch_code": branch_code,
        "created_at": created_at
    })

df_clean_accounts = pd.DataFrame(accounts)
df_raw_accounts = df_clean_accounts.copy()


# -----------------------------------------------------------------------------
# STEP 3: GENERATE TRANSACTIONS DATA (~10,000 Transactions)
# -----------------------------------------------------------------------------
print("Generating 10,000 synthetic banking transactions...")

transactions = []
acc_ids = [a["account_id"] for a in accounts]
acc_opening_map = {a["account_id"]: a["opening_date"] for a in accounts}

start_txn_period = datetime.datetime(2024, 1, 1, 0, 0, 0)
end_txn_period = datetime.datetime(2024, 12, 31, 23, 59, 59)

for i in range(1, 10001):
    transaction_id = f"TXN{i:06d}"
    acc_id = random.choice(acc_ids)
    
    opening_dt_str = acc_opening_map[acc_id]
    opening_dt = datetime.datetime.strptime(opening_dt_str, "%Y-%m-%d")
    
    # Transaction date must be after account opening date
    t_start = max(start_txn_period, opening_dt)
    t_delta_seconds = int((end_txn_period - t_start).total_seconds())
    if t_delta_seconds <= 0:
        random_seconds = 0
    else:
        random_seconds = random.randint(0, t_delta_seconds)
    
    txn_datetime = t_start + datetime.timedelta(seconds=random_seconds)
    txn_date_str = txn_datetime.strftime("%Y-%m-%d %H:%M:%S")

    txn_type = random.choices(["CREDIT", "DEBIT"], weights=[45, 55])[0]
    
    if txn_type == "CREDIT":
        amount = round(random.uniform(500.0, 100000.0), 2)
        description = random.choice(CREDIT_DESCRIPTIONS)
    else:
        amount = round(random.uniform(50.0, 25000.0), 2)
        description = random.choice(DEBIT_DESCRIPTIONS)

    txn_status = random.choices(["SUCCESS", "FAILED", "PENDING"], weights=[92, 5, 3])[0]
    channel = random.choices(["ATM", "ONLINE", "MOBILE", "BRANCH", "UPI"], weights=[20, 30, 30, 5, 15])[0]
    created_at = txn_date_str

    transactions.append({
        "transaction_id": transaction_id,
        "account_id": acc_id,
        "transaction_date": txn_date_str,
        "transaction_type": txn_type,
        "amount": amount,
        "transaction_status": txn_status,
        "description": description,
        "channel": channel,
        "created_at": created_at
    })

df_clean_transactions = pd.DataFrame(transactions)

# Create RAW transactions dataframe with controlled data quality issues for Phase 2
df_raw_transactions = df_clean_transactions.copy()

# Issue 1: Invalid transaction amounts (~10 negative values)
invalid_amount_idx = random.sample(range(10000), 10)
df_raw_transactions.loc[invalid_amount_idx, "amount"] = -500.00

# Issue 2: Invalid status strings (~10 non-standard values)
invalid_status_idx = random.sample(range(10000), 10)
df_raw_transactions.loc[invalid_status_idx, "transaction_status"] = "COMPLETED"


# -----------------------------------------------------------------------------
# STEP 4: SAVE RAW DATASETS TO DATA/RAW/
# -----------------------------------------------------------------------------
customers_raw_path = os.path.join(RAW_DATA_DIR, "customers.csv")
accounts_raw_path = os.path.join(RAW_DATA_DIR, "accounts.csv")
transactions_raw_path = os.path.join(RAW_DATA_DIR, "transactions.csv")

df_raw_customers.to_csv(customers_raw_path, index=False)
df_raw_accounts.to_csv(accounts_raw_path, index=False)
df_raw_transactions.to_csv(transactions_raw_path, index=False)

print(f"Saved RAW CSVs to {RAW_DATA_DIR}:")
print(f" - customers.csv: {len(df_raw_customers)} rows (includes duplicates & missing fields)")
print(f" - accounts.csv: {len(df_raw_accounts)} rows")
print(f" - transactions.csv: {len(df_raw_transactions)} rows (includes invalid amounts & status strings)")


# -----------------------------------------------------------------------------
# STEP 5: GENERATE POSTGRES SEED.SQL FOR CLEAN DATABASE SEEDING
# -----------------------------------------------------------------------------
seed_sql_path = os.path.join(DATABASE_DIR, "seed.sql")

with open(seed_sql_path, "w", encoding="utf-8") as f:
    f.write("-- =============================================================================\n")
    f.write("-- BANKING CUSTOMER 360 - POSTGRES SEED DATA (PHASE 1)\n")
    f.write("-- Clean, referentially valid dataset for initial PostgreSQL population\n")
    f.write("-- =============================================================================\n\n")
    
    f.write("-- Clear existing records before seeding\n")
    f.write("TRUNCATE TABLE transactions, accounts, customers CASCADE;\n\n")
    
    # 1. Customers Insert
    f.write("-- SEED CUSTOMERS (1,000 rows)\n")
    for _, row in df_clean_customers.iterrows():
        email_val = f"'{row['email']}'" if pd.notnull(row['email']) else "NULL"
        phone_val = f"'{row['phone']}'" if pd.notnull(row['phone']) else "NULL"
        f.write(
            f"INSERT INTO customers (customer_id, first_name, last_name, date_of_birth, gender, email, phone, city, state, postal_code, customer_since, customer_status, created_at) "
            f"VALUES ('{row['customer_id']}', '{row['first_name']}', '{row['last_name']}', '{row['date_of_birth']}', '{row['gender']}', {email_val}, {phone_val}, '{row['city']}', '{row['state']}', '{row['postal_code']}', '{row['customer_since']}', '{row['customer_status']}', '{row['created_at']}');\n"
        )
    f.write("\n")

    # 2. Accounts Insert
    f.write("-- SEED ACCOUNTS (1,500 rows)\n")
    for _, row in df_clean_accounts.iterrows():
        f.write(
            f"INSERT INTO accounts (account_id, customer_id, account_type, account_status, opening_date, balance, branch_code, created_at) "
            f"VALUES ('{row['account_id']}', '{row['customer_id']}', '{row['account_type']}', '{row['account_status']}', '{row['opening_date']}', {row['balance']}, '{row['branch_code']}', '{row['created_at']}');\n"
        )
    f.write("\n")

    # 3. Transactions Insert
    f.write("-- SEED TRANSACTIONS (10,000 rows)\n")
    for _, row in df_clean_transactions.iterrows():
        desc_escaped = str(row['description']).replace("'", "''")
        f.write(
            f"INSERT INTO transactions (transaction_id, account_id, transaction_date, transaction_type, amount, transaction_status, description, channel, created_at) "
            f"VALUES ('{row['transaction_id']}', '{row['account_id']}', '{row['transaction_date']}', '{row['transaction_type']}', {row['amount']}, '{row['transaction_status']}', '{desc_escaped}', '{row['channel']}', '{row['created_at']}');\n"
        )

print(f"Generated clean PostgreSQL seed file: {seed_sql_path}")
print("Data generation process completed successfully!")
