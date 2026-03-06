# Data Dictionary

## How to Generate the Dataset

The dataset files are not tracked in Git due to size. To regenerate:
```bash
python src/generate_dataset.py
```

This creates both files below with identical data every time (seed is fixed).

## transactions.csv (600,000 rows)

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | string | Unique ID (TXN00000001) |
| merchant_id | string | Joins to merchants.csv |
| customer_id | string | Customer identifier |
| timestamp | datetime | Transaction datetime (2025) |
| amount_ngn | float | Amount in Nigerian Naira |
| channel | string | POS_Terminal, Mobile_App, Bank_Transfer, USSD, Web_Gateway, Tap_to_Pay, QR_Code |
| card_type | string | Debit_Card, Credit_Card, Prepaid, Virtual_Card |
| status | string | completed, disputed, chargeback, reversed, declined, failed, pending |
| is_fraud | int | 1 = fraud, 0 = legitimate |

Notes: card_type ~2% null, channel ~1% null, fraud rate 3.32%

## merchants.csv (5,000 rows)

| Column | Type | Description |
|--------|------|-------------|
| merchant_id | string | Primary key |
| merchant_name | string | Display name |
| category | string | 15 business categories |
| state | string | Nigerian state (20 states) |
| signup_date | date | Platform join date |