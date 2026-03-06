# Fintech Transaction Intelligence & Merchant Risk Scoring

An end-to-end data analytics and machine learning project analyzing **600,000+ payment transactions** across **5,000 merchants** in the Nigerian fintech ecosystem. Built to identify high-risk merchants, detect transaction anomalies, and power strategic decisions for payment companies.

## Business Problem

Fintech companies processing millions of transactions need to:
1. **Identify high-risk merchants** before chargebacks and fraud erode revenue
2. **Segment merchants into tiers** to allocate monitoring resources efficiently
3. **Detect transaction anomalies** in real-time to prevent revenue leakage

## Dataset

| File | Rows | Description |
|------|------|-------------|
| `transactions.csv` | 600,000 | Payment transactions (Jan-Dec 2025) |
| `merchants.csv` | 5,000 | Merchant profiles with categories and locations |

**Key stats:** N26.3B total volume | 3.32% fraud rate | 7 payment channels | 15 merchant categories | 20 Nigerian states

## Project Structure

```
fintech-merchant-intelligence/
├── README.md
├── requirements.txt
├── app.py                          # Streamlit dashboard
├── notebooks/
│   ├── 01_data_exploration.ipynb   # EDA + initial insights
│   ├── 02_sql_analytics.ipynb      # 20+ SQL queries
│   ├── 03_feature_engineering.ipynb # Merchant-level features
│   └── 04_modeling.ipynb           # Risk model + SHAP
├── sql/
│   ├── schema.sql                  # Table creation DDL
│   ├── merchant_tiering.sql        # NTILE tiering queries
│   └── analytics_queries.sql       # All analytical queries
├── src/
│   ├── data_processing.py          # Cleaning + feature engineering
│   └── model.py                    # Training + prediction
├── reports/
│   └── executive_summary.pdf       # 1-page business report
└── data/
    ├── README.md                   # Data dictionary
    ├── transactions.csv
    └── merchants.csv
```

## Tech Stack

- **Analysis:** Python (Pandas, NumPy), SQL (PostgreSQL)
- **Visualization:** Matplotlib, Seaborn
- **Machine Learning:** Scikit-learn, XGBoost, SHAP
- **Deployment:** Streamlit
- **Database:** PostgreSQL (CTEs, Window Functions, NTILE)

## Key Findings

> _To be updated after analysis_

## Quick Start

```bash
git clone https://github.com/Ethminer001/fintech-merchant-intelligence.git
cd fintech-merchant-intelligence
pip install -r requirements.txt
streamlit run app.py
```

## Contact

**Olowu Abraham Aduragbemi**
- LinkedIn: [linkedin.com/in/eriioluwa](https://linkedin.com/in/eriioluwa)
- GitHub: [github.com/Ethminer001](https://github.com/Ethminer001)
- Email: olowu.tayo200@gmail.com
