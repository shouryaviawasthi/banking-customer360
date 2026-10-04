import os
import pandas as pd
import numpy as np

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REJECTED_DIR = os.path.join(PROCESSED_DIR, "rejected_records")

# Ensure directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REJECTED_DIR, exist_ok=True)

def run_etl_pipeline():
    print("--- Starting ETL Pipeline (Phase 2) ---")
    
    # 1. Load RAW Data
    print("Loading RAW datasets...")
    df_customers = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    df_accounts = pd.read_csv(os.path.join(RAW_DIR, "accounts.csv"))
    df_transactions = pd.read_csv(os.path.join(RAW_DIR, "transactions.csv"))
    
    report_data = []

    # -------------------------------------------------------------
    # 2. Clean Customers Data
    # -------------------------------------------------------------
    print("Processing Customers...")
    initial_cust_count = len(df_customers)
    
    # a. Identify and separate duplicates
    duplicates = df_customers[df_customers.duplicated(subset=['customer_id'], keep='first')]
    df_customers = df_customers.drop_duplicates(subset=['customer_id'], keep='first')
    
    # b. Identify missing emails or phones
    missing_contact = df_customers[df_customers['email'].isna() | df_customers['phone'].isna()]
    df_customers = df_customers.dropna(subset=['email', 'phone'])
    
    # c. Fix inconsistent city names
    if 'city' in df_customers.columns:
        df_customers['city'] = df_customers['city'].astype(str).str.strip().str.title()
        df_customers['city'] = df_customers['city'].replace({'Bangalore': 'Bengaluru'})
    
    # Combine rejected customers
    rejected_customers = pd.concat([duplicates, missing_contact])
    if not rejected_customers.empty:
        rejected_customers.to_csv(os.path.join(REJECTED_DIR, "customers_rejected.csv"), index=False)
    
    report_data.append({
        'Table': 'Customers',
        'Total_Processed': initial_cust_count,
        'Clean_Records': len(df_customers),
        'Rejected_Records': len(rejected_customers),
        'Notes': 'Removed duplicates and missing contact info. Standardized cities.'
    })

    # -------------------------------------------------------------
    # 3. Clean Accounts Data
    # -------------------------------------------------------------
    print("Processing Accounts...")
    initial_acc_count = len(df_accounts)
    
    # (Assuming accounts data is mostly clean, but we can do a simple check)
    invalid_accounts = df_accounts[df_accounts['balance'] < 0]
    df_accounts = df_accounts[df_accounts['balance'] >= 0]
    
    if not invalid_accounts.empty:
        invalid_accounts.to_csv(os.path.join(REJECTED_DIR, "accounts_rejected.csv"), index=False)
        
    report_data.append({
        'Table': 'Accounts',
        'Total_Processed': initial_acc_count,
        'Clean_Records': len(df_accounts),
        'Rejected_Records': len(invalid_accounts),
        'Notes': 'Removed accounts with negative balance.'
    })

    # -------------------------------------------------------------
    # 4. Clean Transactions Data
    # -------------------------------------------------------------
    print("Processing Transactions...")
    initial_txn_count = len(df_transactions)
    
    # a. Invalid / Negative amounts
    invalid_txns = df_transactions[df_transactions['amount'] <= 0]
    df_transactions = df_transactions[df_transactions['amount'] > 0]
    
    if not invalid_txns.empty:
        invalid_txns.to_csv(os.path.join(REJECTED_DIR, "transactions_rejected.csv"), index=False)
        
    # b. Standardize transaction status
    if 'transaction_status' in df_transactions.columns:
        df_transactions['transaction_status'] = df_transactions['transaction_status'].replace({'COMPLETED': 'SUCCESS'})
        
    report_data.append({
        'Table': 'Transactions',
        'Total_Processed': initial_txn_count,
        'Clean_Records': len(df_transactions),
        'Rejected_Records': len(invalid_txns),
        'Notes': 'Removed negative amounts. Standardized COMPLETED to SUCCESS.'
    })

    # -------------------------------------------------------------
    # 5. Save Clean Data
    # -------------------------------------------------------------
    print("Saving clean datasets...")
    df_customers.to_csv(os.path.join(PROCESSED_DIR, "customers_clean.csv"), index=False)
    df_accounts.to_csv(os.path.join(PROCESSED_DIR, "accounts_clean.csv"), index=False)
    df_transactions.to_csv(os.path.join(PROCESSED_DIR, "transactions_clean.csv"), index=False)

    # -------------------------------------------------------------
    # 6. Generate Data Quality Report
    # -------------------------------------------------------------
    df_report = pd.DataFrame(report_data)
    
    # Save as CSV
    df_report.to_csv(os.path.join(PROCESSED_DIR, "data_quality_report.csv"), index=False)
    
    # Save as TXT
    report_txt_path = os.path.join(PROCESSED_DIR, "data_quality_report.txt")
    with open(report_txt_path, 'w') as f:
        f.write("=== DATA QUALITY REPORT ===\n\n")
        for idx, row in df_report.iterrows():
            f.write(f"Table: {row['Table']}\n")
            f.write(f"  - Total Processed: {row['Total_Processed']}\n")
            f.write(f"  - Clean Records: {row['Clean_Records']}\n")
            f.write(f"  - Rejected Records: {row['Rejected_Records']}\n")
            f.write(f"  - Notes: {row['Notes']}\n\n")
            
    print("--- ETL Pipeline Completed Successfully ---")
    print(f"Check {PROCESSED_DIR} for clean data and reports.")

if __name__ == "__main__":
    run_etl_pipeline()
