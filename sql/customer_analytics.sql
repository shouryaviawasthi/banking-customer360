-- =============================================================================
-- BANKING CUSTOMER 360 - CUSTOMER ANALYTICS (PHASE 3)
-- Database: PostgreSQL
-- Description: Customer-level analytics queries using vw_customer_360
-- =============================================================================

-- 1. Total customers
SELECT COUNT(*) AS total_customers FROM vw_customer_360;

-- 2. Active customers (Based on transaction activity)
SELECT COUNT(*) AS active_customers FROM vw_customer_360 WHERE customer_activity_status = 'ACTIVE';

-- 3. Inactive customers
SELECT COUNT(*) AS inactive_customers FROM vw_customer_360 WHERE customer_activity_status = 'INACTIVE';

-- 4. Customers by city
SELECT city, COUNT(*) AS customer_count 
FROM vw_customer_360 
GROUP BY city 
ORDER BY customer_count DESC;

-- 5. Customers by state
SELECT state, COUNT(*) AS customer_count 
FROM vw_customer_360 
GROUP BY state 
ORDER BY customer_count DESC;

-- 6. Customers by status (demographic status vs activity status)
SELECT customer_status, COUNT(*) AS customer_count 
FROM vw_customer_360 
GROUP BY customer_status;

-- 7. Customers by account count
SELECT number_of_accounts, COUNT(*) AS customer_count 
FROM vw_customer_360 
GROUP BY number_of_accounts 
ORDER BY number_of_accounts;

-- 8. Customers with multiple accounts
SELECT customer_id, full_name, number_of_accounts 
FROM vw_customer_360 
WHERE number_of_accounts > 1 
ORDER BY number_of_accounts DESC;

-- 9. Customers with no transactions
SELECT customer_id, full_name, number_of_accounts, total_transactions 
FROM vw_customer_360 
WHERE total_transactions = 0;

-- 10. Top 10 Customers with highest balances (Window Function Example)
WITH RankedCustomers AS (
    SELECT 
        customer_id, 
        full_name, 
        total_balance,
        RANK() OVER (ORDER BY total_balance DESC) as balance_rank
    FROM vw_customer_360
)
SELECT * FROM RankedCustomers WHERE balance_rank <= 10;

-- 11. Top 10 Customers with highest transaction volume
SELECT customer_id, full_name, total_transactions 
FROM vw_customer_360 
ORDER BY total_transactions DESC 
LIMIT 10;

-- 12. Top 10 Customers with highest credit volume
SELECT customer_id, full_name, total_credit 
FROM vw_customer_360 
ORDER BY total_credit DESC 
LIMIT 10;

-- 13. Top 10 Customers with highest debit volume
SELECT customer_id, full_name, total_debit 
FROM vw_customer_360 
ORDER BY total_debit DESC 
LIMIT 10;
