"""
Fintech Transaction Dataset Generator
Generates synthetic Nigerian fintech transaction data for analysis.
Run: python src/generate_dataset.py
Output: data/transactions.csv, data/merchants.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

n_merchants = 5000
n_transactions = 600000

merchant_categories = ['POS_Retail', 'POS_Restaurant', 'POS_Fuel', 'Online_Ecommerce', 'Online_Bills',
                       'Transfer_P2P', 'Transfer_Business', 'POS_Grocery', 'POS_Pharmacy', 'Online_Travel',
                       'POS_Electronics', 'POS_Fashion', 'Online_Gaming', 'POS_Supermarket', 'Transfer_Payroll']

cat_probs = [0.15, 0.08, 0.06, 0.12, 0.08, 0.10, 0.07, 0.10, 0.04, 0.03, 0.05, 0.04, 0.02, 0.04, 0.02]

states = ['Lagos', 'Abuja', 'Rivers', 'Oyo', 'Kano', 'Enugu', 'Delta', 'Kaduna', 'Ogun', 'Edo',
          'Anambra', 'Imo', 'Kwara', 'Osun', 'Ekiti', 'Bayelsa', 'Cross River', 'Plateau', 'Benue', 'Abia']
state_probs = np.array([0.25, 0.12, 0.08, 0.07, 0.06, 0.05, 0.04, 0.04, 0.04, 0.03,
                         0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.03])
state_probs = state_probs / state_probs.sum()

merchant_risk = np.random.beta(2, 8, n_merchants)

merchants = pd.DataFrame({
    'merchant_id': [f'MRC{str(i).zfill(5)}' for i in range(1, n_merchants + 1)],
    'merchant_name': [f'Merchant_{i}' for i in range(1, n_merchants + 1)],
    'category': np.random.choice(merchant_categories, n_merchants, p=cat_probs),
    'state': np.random.choice(states, n_merchants, p=state_probs),
    'signup_date': [datetime(2024, 1, 1) + timedelta(days=int(np.random.exponential(180))) for _ in range(n_merchants)],
    'risk_score_true': merchant_risk,
    'is_flagged': (merchant_risk > 0.4).astype(int),
})

merchant_volume = np.random.pareto(1.5, n_merchants) + 1
merchant_volume = (merchant_volume / merchant_volume.sum() * n_transactions).astype(int)
merchant_volume = np.maximum(merchant_volume, 5)
diff = n_transactions - merchant_volume.sum()
if diff > 0:
    merchant_volume[:diff] += 1
elif diff < 0:
    for i in range(abs(diff)):
        merchant_volume[np.argmax(merchant_volume)] -= 1

print(f"Generating {merchant_volume.sum():,} transactions for {n_merchants} merchants...")

amt_config = {
    'POS_Fuel': (15000, 8000), 'POS_Grocery': (8000, 5000), 'POS_Supermarket': (8000, 5000),
    'POS_Restaurant': (5000, 3000), 'POS_Electronics': (85000, 50000), 'POS_Fashion': (25000, 15000),
    'POS_Pharmacy': (6000, 4000), 'POS_Retail': (10000, 7000),
    'Online_Ecommerce': (35000, 25000), 'Online_Bills': (12000, 8000), 'Online_Travel': (150000, 80000),
    'Online_Gaming': (3000, 2000), 'Transfer_P2P': (20000, 15000), 'Transfer_Business': (250000, 150000),
    'Transfer_Payroll': (180000, 80000),
}

hour_probs = np.array([0.01, 0.005, 0.005, 0.005, 0.005, 0.01, 0.02, 0.04, 0.06, 0.07,
    0.08, 0.08, 0.07, 0.06, 0.06, 0.05, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.02, 0.015])
hour_probs = hour_probs / hour_probs.sum()

start_date = datetime(2025, 1, 1)
date_range_days = 364

all_txns = []
for m_idx in range(n_merchants):
    m = merchants.iloc[m_idx]
    n_txn = merchant_volume[m_idx]
    amt_mean, amt_std = amt_config.get(m['category'], (10000, 7000))

    amounts = np.maximum(np.random.normal(amt_mean, amt_std, n_txn), 100).round(2)
    days_off = np.random.uniform(0, date_range_days, n_txn)
    hours = np.random.choice(24, n_txn, p=hour_probs)
    mins = np.random.randint(0, 60, n_txn)
    timestamps = [start_date + timedelta(days=float(d), hours=int(h), minutes=int(mi))
                  for d, h, mi in zip(days_off, hours, mins)]

    base_fraud = m['risk_score_true'] * 0.15
    fraud_probs = np.full(n_txn, base_fraud)
    fraud_probs[(hours >= 23) | (hours <= 4)] *= 3
    fraud_probs[amounts > (amt_mean + 2.5 * amt_std)] *= 2.5
    fraud_probs = np.minimum(fraud_probs, 0.30)
    is_fraud = np.random.binomial(1, fraud_probs)

    statuses = []
    for f in is_fraud:
        if f:
            statuses.append(np.random.choice(['disputed', 'chargeback', 'reversed'], p=[0.4, 0.35, 0.25]))
        elif np.random.random() < 0.03:
            statuses.append(np.random.choice(['declined', 'failed', 'pending']))
        else:
            statuses.append('completed')

    if m['category'].startswith('POS'):
        channels = np.random.choice(['POS_Terminal', 'Tap_to_Pay', 'QR_Code'], n_txn, p=[0.6, 0.25, 0.15])
    elif m['category'].startswith('Online'):
        channels = np.random.choice(['Web_Gateway', 'Mobile_App', 'USSD'], n_txn, p=[0.45, 0.40, 0.15])
    else:
        channels = np.random.choice(['Bank_Transfer', 'Mobile_App', 'USSD'], n_txn, p=[0.50, 0.35, 0.15])

    card_types = np.random.choice(['Debit_Card', 'Credit_Card', 'Prepaid', 'Virtual_Card'], n_txn, p=[0.55, 0.15, 0.15, 0.15])
    customer_ids = [f'CUS{str(np.random.randint(1, 200000)).zfill(6)}' for _ in range(n_txn)]

    batch = pd.DataFrame({
        'merchant_id': m['merchant_id'], 'customer_id': customer_ids, 'timestamp': timestamps,
        'amount_ngn': amounts, 'channel': channels, 'card_type': card_types,
        'status': statuses, 'is_fraud': is_fraud
    })
    all_txns.append(batch)

    if (m_idx + 1) % 1000 == 0:
        print(f"  {m_idx + 1}/{n_merchants} merchants processed...")

txn_df = pd.concat(all_txns, ignore_index=True).sort_values('timestamp').reset_index(drop=True)
txn_df.insert(0, 'transaction_id', [f'TXN{str(i).zfill(8)}' for i in range(1, len(txn_df) + 1)])

txn_df.loc[np.random.random(len(txn_df)) < 0.02, 'card_type'] = np.nan
txn_df.loc[np.random.random(len(txn_df)) < 0.01, 'channel'] = np.nan

merchants_out = merchants[['merchant_id', 'merchant_name', 'category', 'state', 'signup_date']].copy()
merchants_out['signup_date'] = merchants_out['signup_date'].dt.strftime('%Y-%m-%d')

txn_df.to_csv('data/transactions.csv', index=False)
merchants_out.to_csv('data/merchants.csv', index=False)

print(f"\nDone!")
print(f"Transactions: {len(txn_df):,} rows -> data/transactions.csv")
print(f"Merchants: {len(merchants_out):,} rows -> data/merchants.csv")
print(f"Fraud rate: {txn_df['is_fraud'].mean():.2%}")
print(f"Total volume: NGN {txn_df['amount_ngn'].sum():,.0f}")