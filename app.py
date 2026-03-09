"""
Fintech Merchant Intelligence Dashboard
Streamlit App — Merchant Risk Scoring & Transaction Analytics

Author: Olowu Abraham Aduragbemi
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Merchant Intelligence Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLORS = ['#1a2744', '#0d7377', '#e63946', '#457b9d', '#f4a261', '#2a9d8f', '#264653']

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    txn = pd.read_csv('data/transactions.csv', parse_dates=['timestamp'])
    merchants = pd.read_csv('data/merchants.csv', parse_dates=['signup_date'])
    
    # Try loading risk scores (from Day 4 modeling)
    try:
        risk = pd.read_csv('data/merchant_risk_scores.csv')
    except FileNotFoundError:
        risk = None
    
    # Try loading features
    try:
        features = pd.read_csv('data/merchant_features.csv')
    except FileNotFoundError:
        features = None
    
    return txn, merchants, risk, features

txn, merchants, risk, features = load_data()

# Merge for analysis
df = txn.merge(merchants, on='merchant_id', how='left')

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🏦 Merchant Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Platform Overview", "🔍 Merchant Lookup", "⚠️ Risk Dashboard", "📈 Transaction Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Built by:** Olowu Abraham Aduragbemi")
st.sidebar.markdown("[GitHub](https://github.com/Ethminer001) · [LinkedIn](https://linkedin.com/in/eriioluwa)")

# ============================================================
# PAGE 1: PLATFORM OVERVIEW
# ============================================================
if page == "📊 Platform Overview":
    st.title("📊 Platform Overview")
    st.markdown("Real-time snapshot of the fintech payment ecosystem")
    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    total_volume = txn['amount_ngn'].sum()
    total_txns = len(txn)
    total_merchants = merchants['merchant_id'].nunique()
    fraud_rate = txn['is_fraud'].mean()
    
    col1.metric("Total Volume", f"₦{total_volume/1e9:.1f}B")
    col2.metric("Transactions", f"{total_txns:,}")
    col3.metric("Active Merchants", f"{total_merchants:,}")
    col4.metric("Fraud Rate", f"{fraud_rate:.2%}")
    
    st.markdown("---")
    
    # Row 2: Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Monthly Transaction Volume")
        monthly = txn.set_index('timestamp').resample('M').agg(
            volume=('amount_ngn', 'sum'),
            count=('transaction_id', 'count')
        ).reset_index()
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(monthly['timestamp'], monthly['volume'] / 1e9, color=COLORS[0], alpha=0.8)
        ax.set_ylabel('Volume (₦ Billions)')
        ax.set_title('Monthly Transaction Volume', fontweight='bold')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_right:
        st.subheader("Revenue by Category (Top 10)")
        cat_vol = df.groupby('category')['amount_ngn'].sum().sort_values(ascending=True).tail(10)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(cat_vol.index, cat_vol.values / 1e9, color=COLORS[1])
        ax.set_xlabel('Volume (₦ Billions)')
        ax.set_title('Top 10 Categories by Volume', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    # Row 3
    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        st.subheader("Transaction Status Breakdown")
        status_counts = txn['status'].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 4))
        colors_status = [COLORS[5] if s == 'completed' else COLORS[2] for s in status_counts.index]
        ax.barh(status_counts.index, status_counts.values, color=colors_status)
        ax.set_xlabel('Count')
        ax.set_title('Transaction Status Distribution', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_right2:
        st.subheader("Top 10 States by Volume")
        state_vol = df.groupby('state')['amount_ngn'].sum().sort_values(ascending=True).tail(10)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(state_vol.index, state_vol.values / 1e9, color=COLORS[3])
        ax.set_xlabel('Volume (₦ Billions)')
        ax.set_title('Top States by Transaction Volume', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# ============================================================
# PAGE 2: MERCHANT LOOKUP
# ============================================================
elif page == "🔍 Merchant Lookup":
    st.title("🔍 Merchant Lookup")
    st.markdown("Search any merchant to view their profile, risk score, and transaction history")
    st.markdown("---")
    
    # Search
    merchant_list = sorted(merchants['merchant_id'].tolist())
    selected = st.selectbox("Select Merchant ID", merchant_list, index=0)
    
    if selected:
        m_info = merchants[merchants['merchant_id'] == selected].iloc[0]
        m_txns = txn[txn['merchant_id'] == selected]
        
        # Risk score if available
        risk_score = None
        risk_label = None
        if risk is not None and selected in risk['merchant_id'].values:
            r = risk[risk['merchant_id'] == selected].iloc[0]
            risk_score = r['risk_score']
            risk_label = r['risk_label']
        
        # Profile cards
        st.subheader(f"Merchant Profile: {selected}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Category", m_info['category'])
        col2.metric("State", m_info['state'])
        col3.metric("Signup Date", str(m_info['signup_date'])[:10])
        if risk_score is not None:
            risk_color = "🔴" if risk_score > 0.6 else "🟡" if risk_score > 0.3 else "🟢"
            col4.metric("Risk Score", f"{risk_color} {risk_score:.3f} ({risk_label})")
        else:
            col4.metric("Risk Score", "N/A — Run modeling notebook")
        
        st.markdown("---")
        
        # Transaction KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Transactions", f"{len(m_txns):,}")
        col2.metric("Total Volume", f"₦{m_txns['amount_ngn'].sum():,.0f}")
        col3.metric("Avg Ticket", f"₦{m_txns['amount_ngn'].mean():,.0f}")
        col4.metric("Fraud Rate", f"{m_txns['is_fraud'].mean():.2%}")
        chargeback_rate = (m_txns['status'] == 'chargeback').mean()
        col5.metric("Chargeback Rate", f"{chargeback_rate:.2%}")
        
        st.markdown("---")
        
        # Transaction history chart
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Daily Transaction Volume")
            daily = m_txns.set_index('timestamp').resample('W')['amount_ngn'].sum().reset_index()
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(daily['timestamp'], daily['amount_ngn'], color=COLORS[0], linewidth=1.5)
            ax.fill_between(daily['timestamp'], daily['amount_ngn'], alpha=0.1, color=COLORS[0])
            ax.set_ylabel('Weekly Volume (₦)')
            ax.set_title(f'{selected} — Weekly Transaction Volume', fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col_right:
            st.subheader("Transaction Status Mix")
            status_mix = m_txns['status'].value_counts()
            
            fig, ax = plt.subplots(figsize=(8, 4))
            colors_pie = [COLORS[5] if s == 'completed' else COLORS[2] if s in ['chargeback', 'disputed', 'reversed'] else COLORS[3] for s in status_mix.index]
            ax.pie(status_mix.values, labels=status_mix.index, autopct='%1.1f%%', colors=colors_pie)
            ax.set_title(f'{selected} — Status Breakdown', fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        # Recent transactions table
        st.subheader("Recent Transactions")
        recent = m_txns.sort_values('timestamp', ascending=False).head(20)[
            ['transaction_id', 'timestamp', 'amount_ngn', 'channel', 'card_type', 'status', 'is_fraud']
        ]
        st.dataframe(recent, use_container_width=True, hide_index=True)

# ============================================================
# PAGE 3: RISK DASHBOARD
# ============================================================
elif page == "⚠️ Risk Dashboard":
    st.title("⚠️ Risk Dashboard")
    st.markdown("Merchant risk scoring and monitoring")
    st.markdown("---")
    
    if risk is None:
        st.warning("⚠️ Risk scores not available. Run notebook 04_modeling.ipynb first to generate merchant_risk_scores.csv")
    else:
        # Risk distribution KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        high_risk_count = len(risk[risk['risk_score'] > 0.5])
        high_risk_volume = risk[risk['risk_score'] > 0.5]['total_volume'].sum()
        avg_risk = risk['risk_score'].mean()
        
        col1.metric("High-Risk Merchants", f"{high_risk_count:,}")
        col2.metric("Volume at Risk", f"₦{high_risk_volume/1e9:.2f}B")
        col3.metric("Avg Risk Score", f"{avg_risk:.3f}")
        col4.metric("Total Merchants Scored", f"{len(risk):,}")
        
        st.markdown("---")
        
        # Risk tier breakdown
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Risk Score Distribution")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(risk['risk_score'], bins=50, color=COLORS[0], edgecolor='white', alpha=0.8)
            ax.axvline(0.5, color=COLORS[2], linestyle='--', linewidth=2, label='High-Risk Threshold (0.5)')
            ax.set_xlabel('Risk Score')
            ax.set_ylabel('Merchant Count')
            ax.set_title('Distribution of Merchant Risk Scores', fontweight='bold')
            ax.legend()
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col_right:
            st.subheader("Risk Tier Summary")
            tier_summary = risk.groupby('risk_label').agg(
                merchants=('merchant_id', 'count'),
                total_volume=('total_volume', 'sum'),
                avg_fraud=('fraud_rate', 'mean')
            ).reset_index()
            tier_summary['avg_fraud'] = (tier_summary['avg_fraud'] * 100).round(2)
            tier_summary['total_volume'] = (tier_summary['total_volume'] / 1e9).round(2)
            tier_summary.columns = ['Risk Tier', 'Merchants', 'Volume (₦B)', 'Avg Fraud Rate %']
            st.dataframe(tier_summary, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Top 20 highest risk merchants
        st.subheader("🚨 Top 20 Highest-Risk Merchants")
        top_risk = risk.nlargest(20, 'risk_score')[
            ['merchant_id', 'category', 'state', 'total_txn_count', 'total_volume', 'fraud_rate', 'risk_score', 'risk_label']
        ].copy()
        top_risk['total_volume'] = top_risk['total_volume'].apply(lambda x: f"₦{x:,.0f}")
        top_risk['fraud_rate'] = (top_risk['fraud_rate'] * 100).round(2).astype(str) + '%'
        top_risk['risk_score'] = top_risk['risk_score'].round(4)
        st.dataframe(top_risk, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Risk by category
        col_left2, col_right2 = st.columns(2)
        
        with col_left2:
            st.subheader("Risk Score by Category")
            cat_risk = risk.groupby('category')['risk_score'].mean().sort_values(ascending=True)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            colors_bar = [COLORS[2] if v > 0.3 else COLORS[1] for v in cat_risk.values]
            ax.barh(cat_risk.index, cat_risk.values, color=colors_bar)
            ax.set_xlabel('Average Risk Score')
            ax.set_title('Mean Risk Score by Category', fontweight='bold')
            ax.axvline(0.3, color='gray', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with col_right2:
            st.subheader("Risk Score by State (Top 15)")
            state_risk = risk.groupby('state')['risk_score'].mean().sort_values(ascending=True).tail(15)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            colors_bar = [COLORS[2] if v > 0.3 else COLORS[1] for v in state_risk.values]
            ax.barh(state_risk.index, state_risk.values, color=colors_bar)
            ax.set_xlabel('Average Risk Score')
            ax.set_title('Mean Risk Score by State', fontweight='bold')
            ax.axvline(0.3, color='gray', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

# ============================================================
# PAGE 4: TRANSACTION ANALYTICS
# ============================================================
elif page == "📈 Transaction Analytics":
    st.title("📈 Transaction Analytics")
    st.markdown("Deep-dive into transaction patterns and fraud trends")
    st.markdown("---")
    
    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        categories = ['All'] + sorted(df['category'].unique().tolist())
        sel_cat = st.selectbox("Category", categories)
    
    with col_f2:
        states = ['All'] + sorted(df['state'].unique().tolist())
        sel_state = st.selectbox("State", states)
    
    with col_f3:
        channels = ['All'] + sorted(df['channel'].dropna().unique().tolist())
        sel_channel = st.selectbox("Channel", channels)
    
    # Apply filters
    filtered = df.copy()
    if sel_cat != 'All':
        filtered = filtered[filtered['category'] == sel_cat]
    if sel_state != 'All':
        filtered = filtered[filtered['state'] == sel_state]
    if sel_channel != 'All':
        filtered = filtered[filtered['channel'] == sel_channel]
    
    # Filtered KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transactions", f"{len(filtered):,}")
    col2.metric("Volume", f"₦{filtered['amount_ngn'].sum()/1e9:.2f}B")
    col3.metric("Avg Ticket", f"₦{filtered['amount_ngn'].mean():,.0f}")
    col4.metric("Fraud Rate", f"{filtered['is_fraud'].mean():.2%}")
    
    st.markdown("---")
    
    # Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Hourly Transaction Volume & Fraud Rate")
        filtered['hour'] = filtered['timestamp'].dt.hour
        hourly = filtered.groupby('hour').agg(
            count=('transaction_id', 'count'),
            fraud_rate=('is_fraud', 'mean')
        ).reset_index()
        
        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax2 = ax1.twinx()
        ax1.bar(hourly['hour'], hourly['count'], color=COLORS[0], alpha=0.4)
        ax2.plot(hourly['hour'], hourly['fraud_rate'] * 100, color=COLORS[2], linewidth=2, marker='o')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('Transaction Count')
        ax2.set_ylabel('Fraud Rate (%)')
        ax1.set_title('Hourly Patterns', fontweight='bold')
        ax1.set_xticks(range(24))
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_right:
        st.subheader("Daily Volume Trend")
        daily = filtered.set_index('timestamp').resample('D')['amount_ngn'].sum().reset_index()
        daily['ma7'] = daily['amount_ngn'].rolling(7).mean()
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(daily['timestamp'], daily['amount_ngn'], alpha=0.2, color=COLORS[0])
        ax.plot(daily['timestamp'], daily['ma7'], color=COLORS[1], linewidth=2, label='7-Day MA')
        ax.set_ylabel('Daily Volume (₦)')
        ax.set_title('Daily Transaction Volume', fontweight='bold')
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        st.subheader("Fraud Rate by Channel")
        channel_fraud = filtered.dropna(subset=['channel']).groupby('channel').agg(
            count=('transaction_id', 'count'),
            fraud_rate=('is_fraud', 'mean')
        ).reset_index().sort_values('fraud_rate', ascending=True)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(channel_fraud['channel'], channel_fraud['fraud_rate'] * 100, color=COLORS[1])
        ax.set_xlabel('Fraud Rate (%)')
        ax.set_title('Fraud Rate by Payment Channel', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_right2:
        st.subheader("Amount Distribution")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(np.log10(filtered['amount_ngn'].clip(lower=1)), bins=50, color=COLORS[0], edgecolor='white')
        ax.set_xlabel('Log10(Amount ₦)')
        ax.set_ylabel('Frequency')
        ax.set_title('Transaction Amount Distribution', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    # Heatmap
    st.markdown("---")
    st.subheader("Transaction Heatmap: Hour x Day of Week")
    
    filtered['dow'] = filtered['timestamp'].dt.day_name()
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = filtered.pivot_table(values='transaction_id', index='hour', columns='dow', aggfunc='count')
    heatmap_data = heatmap_data.reindex(columns=dow_order)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(heatmap_data, cmap='YlOrRd', ax=ax, linewidths=0.5)
    ax.set_title('Transaction Volume: Hour x Day of Week', fontweight='bold')
    ax.set_ylabel('Hour of Day')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
