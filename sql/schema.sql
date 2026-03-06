-- Fintech Merchant Intelligence - Database Schema

CREATE TABLE IF NOT EXISTS merchants (
    merchant_id     VARCHAR(10) PRIMARY KEY,
    merchant_name   VARCHAR(100) NOT NULL,
    category        VARCHAR(50) NOT NULL,
    state           VARCHAR(50) NOT NULL,
    signup_date     DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  VARCHAR(15) PRIMARY KEY,
    merchant_id     VARCHAR(10) NOT NULL REFERENCES merchants(merchant_id),
    customer_id     VARCHAR(12) NOT NULL,
    timestamp       TIMESTAMP NOT NULL,
    amount_ngn      NUMERIC(12,2) NOT NULL,
    channel         VARCHAR(20),
    card_type       VARCHAR(20),
    status          VARCHAR(20) NOT NULL,
    is_fraud        SMALLINT NOT NULL DEFAULT 0
);

CREATE INDEX idx_txn_merchant ON transactions(merchant_id);
CREATE INDEX idx_txn_timestamp ON transactions(timestamp);
CREATE INDEX idx_txn_status ON transactions(status);
CREATE INDEX idx_txn_fraud ON transactions(is_fraud);
CREATE INDEX idx_merchant_category ON merchants(category);
CREATE INDEX idx_merchant_state ON merchants(state);
