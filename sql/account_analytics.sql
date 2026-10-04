-- =============================================================================
-- BANKING CUSTOMER 360 - ACCOUNT ANALYTICS (PHASE 3)
-- Database: PostgreSQL
-- Description: Account-level analytics queries
-- =============================================================================

-- 1. Total accounts
SELECT COUNT(*) AS total_accounts FROM accounts;

-- 2. Active accounts
SELECT COUNT(*) AS active_accounts FROM accounts WHERE account_status = 'ACTIVE';

-- 3. Inactive accounts
SELECT COUNT(*) AS inactive_accounts FROM accounts WHERE account_status = 'INACTIVE';

-- 4. Closed accounts
SELECT COUNT(*) AS closed_accounts FROM accounts WHERE account_status = 'CLOSED';

-- 5. Accounts by type
SELECT account_type, COUNT(*) AS total_accounts 
FROM accounts 
GROUP BY account_type 
ORDER BY total_accounts DESC;

-- 6. Accounts by status
SELECT account_status, COUNT(*) AS total_accounts 
FROM accounts 
GROUP BY account_status;

-- 7. Total balance across all accounts
SELECT SUM(balance) AS total_balance FROM accounts;

-- 8. Average balance across all accounts
SELECT AVG(balance) AS average_balance FROM accounts;

-- 9. Minimum balance
SELECT MIN(balance) AS min_balance FROM accounts;

-- 10. Maximum balance
SELECT MAX(balance) AS max_balance FROM accounts;

-- 11. Average accounts per customer
WITH CustomerAccountCounts AS (
    SELECT customer_id, COUNT(account_id) AS account_count
    FROM accounts
    GROUP BY customer_id
)
SELECT AVG(account_count) AS avg_accounts_per_customer 
FROM CustomerAccountCounts;

-- 12. Customers with multiple accounts (Alternative JOIN approach)
SELECT c.customer_id, c.first_name, c.last_name, COUNT(a.account_id) AS account_count
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(a.account_id) > 1
ORDER BY account_count DESC;

-- 13. Average balance by account type
SELECT account_type, AVG(balance) AS avg_balance
FROM accounts
GROUP BY account_type
ORDER BY avg_balance DESC;
