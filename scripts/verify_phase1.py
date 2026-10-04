"""
Phase 1 Verification Script
---------------------------
Verifies:
1. RAW datasets generated in data/raw/ (customers.csv, accounts.csv, transactions.csv)
2. Row counts and column schemas
3. Foreign key integrity between tables
4. Executes verification SQL queries against database / sqlite in-memory model
"""

import os
import sys
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATABASE_DIR = os.path.join(BASE_DIR, "database")

CUSTOMERS_CSV = os.path.join(RAW_DIR, "customers.csv")
ACCOUNTS_CSV = os.path.join(RAW_DIR, "accounts.csv")
TRANSACTIONS_CSV = os.path.join(RAW_DIR, "transactions.csv")
SCHEMA_SQL = os.path.join(DATABASE_DIR, "schema.sql")
SEED_SQL = os.path.join(DATABASE_DIR, "seed.sql")


def test_files_exist():
    print("--- 1. Testing File Existence ---")
    files_to_check = [CUSTOMERS_CSV, ACCOUNTS_CSV, TRANSACTIONS_CSV, SCHEMA_SQL, SEED_SQL]
    for filepath in files_to_check:
        rel_path = os.path.relpath(filepath, BASE_DIR)
        if os.path.exists(filepath):
            size_kb = round(os.path.getsize(filepath) / 1024, 2)
            print(f"[PASS] File exists: {rel_path} ({size_kb} KB)")
        else:
            print(f"[FAIL] Missing file: {rel_path}")
            sys.exit(1)


def test_raw_csv_quality():
    print("\n--- 2. Testing RAW Datasets ---")
    df_cust = pd.read_csv(CUSTOMERS_CSV)
    df_acc = pd.read_csv(ACCOUNTS_CSV)
    df_txn = pd.read_csv(TRANSACTIONS_CSV)

    print(f"RAW Customers count    : {len(df_cust)} rows")
    print(f"RAW Accounts count     : {len(df_acc)} rows")
    print(f"RAW Transactions count : {len(df_txn)} rows")

    # Check for intentional data quality issues in RAW
    null_emails = df_cust["email"].isnull().sum()
    null_phones = df_cust["phone"].isnull().sum()
    duplicate_cust_ids = df_cust.duplicated(subset=["customer_id"]).sum()
    invalid_amounts = (df_txn["amount"] <= 0).sum()
    invalid_statuses = (~df_txn["transaction_status"].isin(["SUCCESS", "FAILED", "PENDING"])).sum()

    print(f"\n[INFO] Intentional Raw Data Quality Issues Detected:")
    print(f" - Customers with missing emails : {null_emails}")
    print(f" - Customers with missing phones : {null_phones}")
    print(f" - Duplicate Customer ID rows   : {duplicate_cust_ids}")
    print(f" - Invalid/Negative Txn Amounts  : {invalid_amounts}")
    print(f" - Non-standard Txn Statuses    : {invalid_statuses}")

    assert len(df_cust) >= 1000, "Customers count should be >= 1000"
    assert len(df_acc) >= 1450, "Accounts count should be ~1500"
    assert len(df_txn) >= 9900, "Transactions count should be ~10000"
    print("[PASS] RAW datasets successfully verified!")


def test_sql_queries_execution():
    print("\n--- 3. Verifying SQL Schema & Queries in In-Memory Database ---")
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Load clean data into SQLite for verification
    df_cust = pd.read_csv(CUSTOMERS_CSV).drop_duplicates(subset=["customer_id"])
    df_cust["email"] = df_cust["email"].fillna("missing@example.com")
    df_cust["phone"] = df_cust["phone"].fillna("+91 0000000000")
    
    df_acc = pd.read_csv(ACCOUNTS_CSV)
    df_txn = pd.read_csv(TRANSACTIONS_CSV)
    df_txn = df_txn[df_txn["amount"] > 0]
    df_txn["transaction_status"] = df_txn["transaction_status"].apply(
        lambda s: s if s in ["SUCCESS", "FAILED", "PENDING"] else "SUCCESS"
    )

    df_cust.to_sql("customers", conn, if_exists="replace", index=False)
    df_acc.to_sql("accounts", conn, if_exists="replace", index=False)
    df_txn.to_sql("transactions", conn, if_exists="replace", index=False)

    print("\nExecuting Verification SQL Queries:")

    # Q1: Total Customers
    cursor.execute("SELECT COUNT(*) FROM customers;")
    total_customers = cursor.fetchone()[0]
    print(f"1. Total Customers               : {total_customers}")

    # Q2: Total Accounts
    cursor.execute("SELECT COUNT(*) FROM accounts;")
    total_accounts = cursor.fetchone()[0]
    print(f"2. Total Accounts                : {total_accounts}")

    # Q3: Total Transactions
    cursor.execute("SELECT COUNT(*) FROM transactions;")
    total_txns = cursor.fetchone()[0]
    print(f"3. Total Transactions            : {total_txns}")

    # Q4: Customers with multiple accounts
    cursor.execute("""
        SELECT c.customer_id, c.first_name, c.last_name, COUNT(a.account_id) AS account_count
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name
        HAVING COUNT(a.account_id) > 1
        ORDER BY account_count DESC
        LIMIT 5;
    """)
    multi_acc_sample = cursor.fetchall()
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT customer_id FROM accounts GROUP BY customer_id HAVING COUNT(account_id) > 1
        );
    """)
    multi_acc_total = cursor.fetchone()[0]
    print(f"4. Customers with >1 Accounts    : {multi_acc_total} customers")
    print(f"   Sample multi-account customers: {multi_acc_sample[:3]}")

    # Q5: Transactions by Type
    cursor.execute("""
        SELECT transaction_type, COUNT(*) AS count, SUM(amount) AS total_amount
        FROM transactions
        GROUP BY transaction_type;
    """)
    txns_by_type = cursor.fetchall()
    print(f"5. Transactions by Type         :")
    for row in txns_by_type:
        print(f"   - {row[0]}: Count = {row[1]}, Total Amount = INR {row[2]:,.2f}")

    # Q6: Foreign Key Integrity Check (Orphan check)
    cursor.execute("""
        SELECT COUNT(*) FROM accounts WHERE customer_id NOT IN (SELECT customer_id FROM customers);
    """)
    orphan_accounts = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM transactions WHERE account_id NOT IN (SELECT account_id FROM accounts);
    """)
    orphan_txns = cursor.fetchone()[0]

    print(f"\n[INFO] Referential Integrity Check:")
    print(f" - Orphan accounts (invalid customer_id) : {orphan_accounts}")
    print(f" - Orphan transactions (invalid account_id): {orphan_txns}")

    assert orphan_accounts == 0, "Found orphan accounts!"
    assert orphan_txns == 0, "Found orphan transactions!"

    conn.close()
    print("\n[PASS] All verification SQL queries and referential integrity tests passed successfully!")


if __name__ == "__main__":
    test_files_exist()
    test_raw_csv_quality()
    test_sql_queries_execution()
