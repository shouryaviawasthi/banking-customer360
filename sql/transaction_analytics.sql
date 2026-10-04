-- =============================================================================
-- BANKING CUSTOMER 360 - TRANSACTION ANALYTICS (PHASE 3)
-- Database: PostgreSQL
-- Description: Transaction-level analytics queries
-- =============================================================================

-- 1. Total transactions
SELECT COUNT(*) AS total_transactions FROM transactions;

-- 2. Successful transactions
SELECT COUNT(*) AS successful_transactions FROM transactions WHERE transaction_status = 'SUCCESS';

-- 3. Failed transactions
SELECT COUNT(*) AS failed_transactions FROM transactions WHERE transaction_status = 'FAILED';

-- 4. Pending transactions
SELECT COUNT(*) AS pending_transactions FROM transactions WHERE transaction_status = 'PENDING';

-- 5. Total transaction amount (Successful only)
SELECT SUM(amount) AS total_transaction_amount FROM transactions WHERE transaction_status = 'SUCCESS';

-- 6. Total credit amount
SELECT SUM(amount) AS total_credit_amount FROM transactions WHERE transaction_type = 'CREDIT' AND transaction_status = 'SUCCESS';

-- 7. Total debit amount
SELECT SUM(amount) AS total_debit_amount FROM transactions WHERE transaction_type = 'DEBIT' AND transaction_status = 'SUCCESS';

-- 8. Average transaction amount
SELECT AVG(amount) AS avg_transaction_amount FROM transactions WHERE transaction_status = 'SUCCESS';

-- 9. Minimum transaction
SELECT MIN(amount) AS min_transaction FROM transactions WHERE transaction_status = 'SUCCESS';

-- 10. Maximum transaction
SELECT MAX(amount) AS max_transaction FROM transactions WHERE transaction_status = 'SUCCESS';

-- 11. Transactions by type
SELECT transaction_type, COUNT(*) AS txn_count, SUM(amount) AS txn_volume 
FROM transactions 
WHERE transaction_status = 'SUCCESS'
GROUP BY transaction_type;

-- 12. Transactions by channel
SELECT channel, COUNT(*) AS txn_count, SUM(amount) AS txn_volume 
FROM transactions 
WHERE transaction_status = 'SUCCESS'
GROUP BY channel 
ORDER BY txn_volume DESC;

-- 13. Transactions by status
SELECT transaction_status, COUNT(*) AS txn_count 
FROM transactions 
GROUP BY transaction_status;

-- 14. Daily transaction volume
SELECT DATE(transaction_date) AS txn_date, COUNT(*) AS txn_count, SUM(amount) AS daily_volume
FROM transactions
WHERE transaction_status = 'SUCCESS'
GROUP BY DATE(transaction_date)
ORDER BY txn_date DESC
LIMIT 30;

-- 15. Monthly transaction volume
SELECT TO_CHAR(transaction_date, 'YYYY-MM') AS txn_month, COUNT(*) AS txn_count, SUM(amount) AS monthly_volume
FROM transactions
WHERE transaction_status = 'SUCCESS'
GROUP BY TO_CHAR(transaction_date, 'YYYY-MM')
ORDER BY txn_month DESC;

-- 16. Monthly credit vs debit
SELECT 
    TO_CHAR(transaction_date, 'YYYY-MM') AS txn_month,
    SUM(CASE WHEN transaction_type = 'CREDIT' THEN amount ELSE 0 END) AS credit_volume,
    SUM(CASE WHEN transaction_type = 'DEBIT' THEN amount ELSE 0 END) AS debit_volume
FROM transactions
WHERE transaction_status = 'SUCCESS'
GROUP BY TO_CHAR(transaction_date, 'YYYY-MM')
ORDER BY txn_month DESC;

-- 17. Most active accounts (by transaction count)
SELECT account_id, COUNT(*) AS txn_count, SUM(amount) AS total_volume
FROM transactions
WHERE transaction_status = 'SUCCESS'
GROUP BY account_id
ORDER BY txn_count DESC
LIMIT 10;

-- 18. Most active customers (by transaction count via JOIN)
SELECT c.customer_id, c.first_name, c.last_name, COUNT(t.transaction_id) AS txn_count
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
JOIN transactions t ON a.account_id = t.account_id
WHERE t.transaction_status = 'SUCCESS'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY txn_count DESC
LIMIT 10;
