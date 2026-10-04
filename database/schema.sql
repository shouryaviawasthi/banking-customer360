-- =============================================================================
-- BANKING CUSTOMER 360 & DATA QUALITY - DATABASE SCHEMA (PHASE 1)
-- Database: PostgreSQL
-- Description: Core relational schema for Customers, Accounts, and Transactions
-- =============================================================================

-- Drop tables if they already exist (in reverse dependency order)
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- -----------------------------------------------------------------------------
-- 1. CUSTOMERS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id     VARCHAR(20)     PRIMARY KEY,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    date_of_birth   DATE            NOT NULL,
    gender          VARCHAR(10)     NOT NULL,
    email           VARCHAR(100),
    phone           VARCHAR(20),
    city            VARCHAR(50)     NOT NULL,
    state           VARCHAR(50)     NOT NULL,
    postal_code     VARCHAR(10)     NOT NULL,
    customer_since  DATE            NOT NULL,
    customer_status VARCHAR(20)     NOT NULL CHECK (customer_status IN ('ACTIVE', 'INACTIVE')),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 2. ACCOUNTS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE accounts (
    account_id      VARCHAR(20)     PRIMARY KEY,
    customer_id     VARCHAR(20)     NOT NULL,
    account_type    VARCHAR(20)     NOT NULL CHECK (account_type IN ('SAVINGS', 'CURRENT', 'SALARY')),
    account_status  VARCHAR(20)     NOT NULL CHECK (account_status IN ('ACTIVE', 'INACTIVE', 'CLOSED')),
    opening_date    DATE            NOT NULL,
    balance         NUMERIC(15, 2)  NOT NULL CHECK (balance >= 0),
    branch_code     VARCHAR(20)     NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_accounts_customer 
        FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) 
        ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- 3. TRANSACTIONS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE transactions (
    transaction_id     VARCHAR(20)     PRIMARY KEY,
    account_id         VARCHAR(20)     NOT NULL,
    transaction_date   TIMESTAMP       NOT NULL,
    transaction_type   VARCHAR(20)     NOT NULL CHECK (transaction_type IN ('CREDIT', 'DEBIT')),
    amount             NUMERIC(12, 2)  NOT NULL CHECK (amount > 0),
    transaction_status VARCHAR(20)     NOT NULL CHECK (transaction_status IN ('SUCCESS', 'FAILED', 'PENDING')),
    description        VARCHAR(255),
    channel            VARCHAR(20)     NOT NULL CHECK (channel IN ('ATM', 'ONLINE', 'MOBILE', 'BRANCH', 'UPI')),
    created_at         TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_transactions_account 
        FOREIGN KEY (account_id) 
        REFERENCES accounts(account_id) 
        ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- -----------------------------------------------------------------------------
-- Foreign Key index for customer -> accounts lookups
CREATE INDEX idx_accounts_customer_id ON accounts(customer_id);

-- Foreign Key index for account -> transactions lookups
CREATE INDEX idx_transactions_account_id ON transactions(account_id);

-- Time-series analytics index for transaction history queries
CREATE INDEX idx_transactions_date ON transactions(transaction_date);

-- Filter index for credit/debit transaction segmentation
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
