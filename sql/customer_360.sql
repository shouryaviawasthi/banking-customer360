-- =============================================================================
-- BANKING CUSTOMER 360 - CUSTOMER 360 VIEW (PHASE 3)
-- Database: PostgreSQL
-- Description: Consolidated 360-degree view of customers, accounts, and 
--              transactions. Uses pre-aggregation to prevent double counting.
-- =============================================================================

CREATE OR REPLACE VIEW vw_customer_360 AS
WITH customer_accounts AS (
    SELECT 
        customer_id,
        COUNT(account_id) AS number_of_accounts,
        SUM(CASE WHEN account_status = 'ACTIVE' THEN 1 ELSE 0 END) AS active_accounts,
        SUM(balance) AS total_balance,
        AVG(balance) AS average_account_balance
    FROM accounts
    GROUP BY customer_id
),
customer_transactions AS (
    SELECT 
        a.customer_id,
        COUNT(t.transaction_id) AS total_transactions,
        SUM(CASE WHEN t.transaction_status = 'SUCCESS' THEN 1 ELSE 0 END) AS successful_transactions,
        SUM(CASE WHEN t.transaction_type = 'CREDIT' AND t.transaction_status = 'SUCCESS' THEN t.amount ELSE 0 END) AS total_credit,
        SUM(CASE WHEN t.transaction_type = 'DEBIT' AND t.transaction_status = 'SUCCESS' THEN t.amount ELSE 0 END) AS total_debit,
        AVG(CASE WHEN t.transaction_status = 'SUCCESS' THEN t.amount ELSE NULL END) AS average_transaction_amount,
        MAX(t.transaction_date) AS last_transaction_date,
        -- Business Rule: ACTIVE if at least one SUCCESSFUL transaction in the last 90 days.
        MAX(CASE WHEN t.transaction_status = 'SUCCESS' AND t.transaction_date >= CURRENT_DATE - INTERVAL '90 days' THEN 1 ELSE 0 END) AS has_recent_activity
    FROM accounts a
    LEFT JOIN transactions t ON a.account_id = t.account_id
    GROUP BY a.customer_id
)
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS full_name,
    c.city,
    c.state,
    c.customer_status,
    c.customer_since,
    COALESCE(ca.number_of_accounts, 0) AS number_of_accounts,
    COALESCE(ca.active_accounts, 0) AS active_accounts,
    COALESCE(ca.total_balance, 0) AS total_balance,
    COALESCE(ca.average_account_balance, 0) AS average_account_balance,
    COALESCE(ct.total_transactions, 0) AS total_transactions,
    COALESCE(ct.successful_transactions, 0) AS successful_transactions,
    COALESCE(ct.total_credit, 0) AS total_credit,
    COALESCE(ct.total_debit, 0) AS total_debit,
    ct.average_transaction_amount,
    ct.last_transaction_date,
    CASE 
        WHEN ct.has_recent_activity = 1 THEN 'ACTIVE'
        ELSE 'INACTIVE'
    END AS customer_activity_status
FROM customers c
LEFT JOIN customer_accounts ca ON c.customer_id = ca.customer_id
LEFT JOIN customer_transactions ct ON c.customer_id = ct.customer_id;
