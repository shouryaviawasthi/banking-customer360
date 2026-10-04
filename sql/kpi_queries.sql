-- =============================================================================
-- BANKING CUSTOMER 360 - KPI LAYER (PHASE 3)
-- Database: PostgreSQL
-- Description: Centralized KPI queries for dashboards (Outputting single rows)
-- =============================================================================

CREATE OR REPLACE VIEW vw_kpi_dashboard AS
SELECT
    -- ==========================================
    -- CUSTOMER KPIs
    -- ==========================================
    (SELECT COUNT(*) FROM vw_customer_360) AS total_customers,
    (SELECT COUNT(*) FROM vw_customer_360 WHERE customer_activity_status = 'ACTIVE') AS active_customers,
    (SELECT COUNT(*) FROM vw_customer_360 WHERE customer_activity_status = 'INACTIVE') AS inactive_customers,
    ROUND((SELECT COUNT(*)::NUMERIC FROM vw_customer_360 WHERE customer_activity_status = 'ACTIVE') / 
          NULLIF((SELECT COUNT(*)::NUMERIC FROM vw_customer_360), 0) * 100, 2) AS active_customer_percentage,

    -- ==========================================
    -- ACCOUNT KPIs
    -- ==========================================
    (SELECT COUNT(*) FROM accounts) AS total_accounts,
    (SELECT COUNT(*) FROM accounts WHERE account_status = 'ACTIVE') AS active_accounts,
    (SELECT COUNT(*) FROM accounts WHERE account_status = 'INACTIVE') AS inactive_accounts,
    (SELECT COUNT(*) FROM accounts WHERE account_status = 'CLOSED') AS closed_accounts,
    (SELECT SUM(balance) FROM accounts) AS total_balance,
    (SELECT AVG(balance) FROM accounts) AS average_account_balance,

    -- ==========================================
    -- TRANSACTION KPIs
    -- ==========================================
    (SELECT COUNT(*) FROM transactions) AS total_transactions,
    (SELECT COUNT(*) FROM transactions WHERE transaction_status = 'SUCCESS') AS successful_transactions,
    (SELECT COUNT(*) FROM transactions WHERE transaction_status = 'FAILED') AS failed_transactions,
    (SELECT COUNT(*) FROM transactions WHERE transaction_status = 'PENDING') AS pending_transactions,
    (SELECT SUM(amount) FROM transactions WHERE transaction_status = 'SUCCESS') AS total_transaction_amount,
    (SELECT SUM(amount) FROM transactions WHERE transaction_type = 'CREDIT' AND transaction_status = 'SUCCESS') AS total_credit_amount,
    (SELECT SUM(amount) FROM transactions WHERE transaction_type = 'DEBIT' AND transaction_status = 'SUCCESS') AS total_debit_amount,
    (SELECT AVG(amount) FROM transactions WHERE transaction_status = 'SUCCESS') AS average_transaction_amount,
    
    -- ==========================================
    -- DATA QUALITY KPIs (Hardcoded Phase 2 Results summary for dashboard layer)
    -- ==========================================
    -- In a real production system, this could query a metadata/audit table.
    1005 AS total_raw_customers,
    965 AS valid_customers,
    40 AS rejected_customers,
    45 AS missing_records_detected,
    5 AS duplicate_records_detected,
    100.0 AS data_quality_score -- Example placeholder score
;

-- Query the KPI View
-- SELECT * FROM vw_kpi_dashboard;
