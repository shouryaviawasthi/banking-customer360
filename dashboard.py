import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pg8000.dbapi
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'config', '.env'))

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Banking Customer 360",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; color: #ffffff; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a1d2e; }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e2140, #252b4a);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border-left: 4px solid;
        margin-bottom: 10px;
    }
    .kpi-value { font-size: 28px; font-weight: 700; margin: 4px 0; }
    .kpi-label { font-size: 13px; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-delta { font-size: 12px; margin-top: 4px; }

    /* Section headers */
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #e2e8f0;
        margin: 20px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #2d3748;
    }

    /* Badge */
    .badge-active { background:#16a34a; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; }
    .badge-inactive { background:#dc2626; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; }

    /* Metric override */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2140, #252b4a);
        border-radius: 10px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DB CONNECTION
# ─────────────────────────────────────────────
@st.cache_resource
def get_conn():
    try:
        return pg8000.dbapi.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "banking_customer360"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "12345678")
        )
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

@st.cache_data(ttl=300)
def fetch(query):
    conn = get_conn()
    if conn:
        try:
            return pd.read_sql(query, conn)
        except Exception as e:
            st.error(f"Query error: {e}")
    return pd.DataFrame()

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Banking 360")
    st.markdown("**Customer Analytics Platform**")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["📊 Overview", "👥 Customers", "🏧 Accounts", "💳 Transactions", "🔍 Data Quality"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Database:** `banking_customer360`")
    st.markdown("**Engine:** PostgreSQL 16")

# ─────────────────────────────────────────────
# FETCH CORE KPIs
# ─────────────────────────────────────────────
kpi_df = fetch("SELECT * FROM vw_kpi_dashboard;")
if kpi_df.empty:
    st.error("❌ No data found. Please ensure the database is seeded and views exist.")
    st.stop()

k = kpi_df.iloc[0]

# ═══════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("# 📊 Overview Dashboard")
    st.caption("A 360° snapshot of your entire banking customer base")
    st.markdown("---")

    # ── Row 1: Customer KPIs
    st.markdown('<div class="section-header">👥 Customer Metrics</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Customers", f"{int(k['total_customers']):,}", help="All customers in the system")
    with c2:
        st.metric("Active Customers", f"{int(k['active_customers']):,}", 
                  delta=f"{k['active_customer_percentage']}% of total",
                  help="Had a successful transaction in the last 90 days")
    with c3:
        st.metric("Inactive Customers", f"{int(k['inactive_customers']):,}",
                  delta=f"{round(100 - float(k['active_customer_percentage']), 2)}% of total",
                  delta_color="inverse",
                  help="No successful transaction in the last 90 days")
    with c4:
        st.metric("Total Balance (₹)", f"₹{float(k['total_balance']):,.0f}", help="Combined balance across all accounts")

    st.markdown("---")

    # ── Row 2: Account & Transaction KPIs
    st.markdown('<div class="section-header">🏧 Account & Transaction Metrics</div>', unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric("Total Accounts", f"{int(k['total_accounts']):,}")
    with c6:
        st.metric("Total Transactions", f"{int(k['total_transactions']):,}")
    with c7:
        st.metric("Successful Transactions", f"{int(k['successful_transactions']):,}",
                  delta=f"{round(int(k['successful_transactions'])/int(k['total_transactions'])*100, 1)}% success rate")
    with c8:
        st.metric("Avg Transaction (₹)", f"₹{float(k['average_transaction_amount']):,.0f}")

    st.markdown("---")

    # ── Row 3: Charts
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown('<div class="section-header">Active vs Inactive Customers</div>', unsafe_allow_html=True)
        act_df = pd.DataFrame({
            "Status": ["Active", "Inactive"],
            "Count": [int(k['active_customers']), int(k['inactive_customers'])]
        })
        fig = px.pie(act_df, values="Count", names="Status", hole=0.55,
                     color="Status",
                     color_discrete_map={"Active": "#16a34a", "Inactive": "#dc2626"})
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0", margin=dict(t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        fig.update_traces(textfont_color="#ffffff")
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        st.markdown('<div class="section-header">Account Status Breakdown</div>', unsafe_allow_html=True)
        acc_status = pd.DataFrame({
            "Status": ["Active", "Inactive", "Closed"],
            "Count": [int(k['active_accounts']), int(k['inactive_accounts']), int(k['closed_accounts'])]
        })
        fig2 = px.bar(acc_status, x="Status", y="Count", color="Status",
                      color_discrete_map={"Active": "#3b82f6", "Inactive": "#f59e0b", "Closed": "#dc2626"},
                      text_auto=True)
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0", showlegend=False, margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Monthly trend
    st.markdown('<div class="section-header">📈 Monthly Credit vs Debit Trend</div>', unsafe_allow_html=True)
    trend = fetch("""
        SELECT TO_CHAR(transaction_date, 'YYYY-MM') AS month,
               SUM(CASE WHEN transaction_type='CREDIT' THEN amount ELSE 0 END) AS credit,
               SUM(CASE WHEN transaction_type='DEBIT'  THEN amount ELSE 0 END) AS debit
        FROM transactions WHERE transaction_status='SUCCESS'
        GROUP BY month ORDER BY month;
    """)
    if not trend.empty:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=trend['month'], y=trend['credit'], name='Credit ₹',
                                  line=dict(color='#3b82f6', width=2.5), fill='tozeroy', fillcolor='rgba(59,130,246,0.1)'))
        fig3.add_trace(go.Scatter(x=trend['month'], y=trend['debit'], name='Debit ₹',
                                  line=dict(color='#f87171', width=2.5), fill='tozeroy', fillcolor='rgba(248,113,113,0.1)'))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0", height=320,
            xaxis=dict(gridcolor='#2d3748'), yaxis=dict(gridcolor='#2d3748'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════
# PAGE 2 — CUSTOMERS
# ═══════════════════════════════════════════════
elif page == "👥 Customers":
    st.markdown("# 👥 Customer Analytics")
    st.caption("Detailed breakdown of customer activity, geography, and rankings")
    st.markdown("---")

    # Activity filter
    filter_status = st.selectbox("Filter by Activity Status", ["All", "ACTIVE", "INACTIVE"])
    
    cust_query = "SELECT * FROM vw_customer_360"
    if filter_status != "All":
        cust_query += f" WHERE customer_activity_status = '{filter_status}'"
    cust_query += " ORDER BY total_balance DESC LIMIT 500;"
    
    cust_df = fetch(cust_query)

    if not cust_df.empty:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Showing Customers", len(cust_df))
        with c2:
            active_shown = len(cust_df[cust_df['customer_activity_status'] == 'ACTIVE'])
            st.metric("Active in View", active_shown)
        with c3:
            st.metric("Total Balance Shown", f"₹{cust_df['total_balance'].sum():,.0f}")

        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown('<div class="section-header">Top 10 Cities by Customer Count</div>', unsafe_allow_html=True)
            city_df = fetch("""
                SELECT city, COUNT(*) AS customers, 
                       SUM(CASE WHEN customer_activity_status='ACTIVE' THEN 1 ELSE 0 END) AS active
                FROM vw_customer_360 GROUP BY city ORDER BY customers DESC LIMIT 10;
            """)
            fig = px.bar(city_df, x='customers', y='city', orientation='h',
                         color='active', color_continuous_scale='Blues', text='customers')
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font_color="#e2e8f0", yaxis=dict(autorange="reversed"),
                              coloraxis_colorbar=dict(title="Active"), margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with ch2:
            st.markdown('<div class="section-header">Customers by Account Count</div>', unsafe_allow_html=True)
            acc_count_df = fetch("""
                SELECT number_of_accounts::text AS accounts, COUNT(*) AS customers
                FROM vw_customer_360 GROUP BY number_of_accounts ORDER BY number_of_accounts;
            """)
            fig2 = px.bar(acc_count_df, x='accounts', y='customers', text_auto=True,
                          color='customers', color_continuous_scale='Viridis')
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#e2e8f0", showlegend=False, margin=dict(t=10, b=10),
                               xaxis_title="Number of Accounts", yaxis_title="Customer Count")
            st.plotly_chart(fig2, use_container_width=True)

        # Top customers table
        st.markdown('<div class="section-header">🏆 Top 20 Customers by Total Balance</div>', unsafe_allow_html=True)
        top_cust = cust_df[['customer_id','full_name','city','state','number_of_accounts',
                             'total_balance','total_transactions','customer_activity_status']].head(20).copy()
        top_cust['total_balance'] = top_cust['total_balance'].apply(lambda x: f"₹{float(x):,.2f}")
        top_cust['customer_activity_status'] = top_cust['customer_activity_status'].apply(
            lambda s: f"🟢 Active" if s == 'ACTIVE' else "🔴 Inactive"
        )
        top_cust.columns = ['Customer ID','Name','City','State','Accounts','Balance','Transactions','Status']
        st.dataframe(top_cust, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════
# PAGE 3 — ACCOUNTS
# ═══════════════════════════════════════════════
elif page == "🏧 Accounts":
    st.markdown("# 🏧 Account Analytics")
    st.caption("Balance distribution, account types, and portfolio overview")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Accounts", f"{int(k['total_accounts']):,}")
    with c2:
        st.metric("Active", f"{int(k['active_accounts']):,}", delta="Operational")
    with c3:
        st.metric("Inactive", f"{int(k['inactive_accounts']):,}", delta_color="inverse", delta="Dormant")
    with c4:
        st.metric("Closed", f"{int(k['closed_accounts']):,}", delta_color="off", delta="Terminated")

    st.markdown("---")

    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown('<div class="section-header">Balance by Account Type</div>', unsafe_allow_html=True)
        acc_type = fetch("""
            SELECT account_type,
                   COUNT(*) AS total_accounts,
                   SUM(balance) AS total_balance,
                   AVG(balance) AS avg_balance
            FROM accounts GROUP BY account_type;
        """)
        fig = px.bar(acc_type, x='account_type', y='total_balance', text_auto=True,
                     color='account_type',
                     color_discrete_map={'SAVINGS':'#3b82f6','CURRENT':'#f59e0b','SALARY':'#10b981'})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", showlegend=False,
                          xaxis_title="Account Type", yaxis_title="Total Balance (₹)",
                          margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        st.markdown('<div class="section-header">Account Distribution by Type</div>', unsafe_allow_html=True)
        fig2 = px.pie(acc_type, values='total_accounts', names='account_type', hole=0.4,
                      color='account_type',
                      color_discrete_map={'SAVINGS':'#3b82f6','CURRENT':'#f59e0b','SALARY':'#10b981'})
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#e2e8f0", margin=dict(t=10, b=10))
        fig2.update_traces(textfont_color="#ffffff")
        st.plotly_chart(fig2, use_container_width=True)

    # Avg balance table
    st.markdown('<div class="section-header">📊 Average Balance by Account Type</div>', unsafe_allow_html=True)
    acc_type['avg_balance'] = acc_type['avg_balance'].apply(lambda x: f"₹{float(x):,.2f}")
    acc_type['total_balance'] = acc_type['total_balance'].apply(lambda x: f"₹{float(x):,.2f}")
    acc_type.columns = ['Account Type', 'Total Accounts', 'Total Balance', 'Average Balance']
    st.dataframe(acc_type, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════
# PAGE 4 — TRANSACTIONS
# ═══════════════════════════════════════════════
elif page == "💳 Transactions":
    st.markdown("# 💳 Transaction Analytics")
    st.caption("Transaction trends, channel breakdown, and volume analysis")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Transactions", f"{int(k['total_transactions']):,}")
    with c2:
        st.metric("✅ Successful", f"{int(k['successful_transactions']):,}")
    with c3:
        st.metric("❌ Failed", f"{int(k['failed_transactions']):,}")
    with c4:
        st.metric("⏳ Pending", f"{int(k['pending_transactions']):,}")

    st.markdown("---")

    c5, c6, c7 = st.columns(3)
    with c5:
        st.metric("Total Credit (₹)", f"₹{float(k['total_credit_amount']):,.0f}")
    with c6:
        st.metric("Total Debit (₹)", f"₹{float(k['total_debit_amount']):,.0f}")
    with c7:
        st.metric("Avg Transaction (₹)", f"₹{float(k['average_transaction_amount']):,.0f}")

    st.markdown("---")

    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown('<div class="section-header">Transactions by Channel</div>', unsafe_allow_html=True)
        ch_df = fetch("""
            SELECT channel, COUNT(*) AS count, SUM(amount) AS volume
            FROM transactions WHERE transaction_status='SUCCESS'
            GROUP BY channel ORDER BY volume DESC;
        """)
        fig = px.bar(ch_df, x='channel', y='count', color='volume',
                     color_continuous_scale='Blues', text_auto=True)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", showlegend=False,
                          xaxis_title="Channel", yaxis_title="Transaction Count",
                          margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        st.markdown('<div class="section-header">Transaction Status Split</div>', unsafe_allow_html=True)
        status_df = fetch("SELECT transaction_status, COUNT(*) AS count FROM transactions GROUP BY transaction_status;")
        fig2 = px.pie(status_df, values='count', names='transaction_status', hole=0.45,
                      color='transaction_status',
                      color_discrete_map={'SUCCESS':'#16a34a','FAILED':'#dc2626','PENDING':'#f59e0b'})
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#e2e8f0", margin=dict(t=10, b=10))
        fig2.update_traces(textfont_color="#ffffff")
        st.plotly_chart(fig2, use_container_width=True)

    # Monthly trend
    st.markdown('<div class="section-header">📈 Monthly Transaction Volume</div>', unsafe_allow_html=True)
    trend = fetch("""
        SELECT TO_CHAR(transaction_date, 'YYYY-MM') AS month, COUNT(*) AS count, SUM(amount) AS volume
        FROM transactions WHERE transaction_status='SUCCESS'
        GROUP BY month ORDER BY month;
    """)
    if not trend.empty:
        fig3 = px.area(trend, x='month', y='volume', labels={'month':'Month','volume':'Volume (₹)'})
        fig3.update_traces(fillcolor='rgba(59,130,246,0.15)', line_color='#3b82f6')
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#e2e8f0", margin=dict(t=10, b=10),
                           xaxis=dict(gridcolor='#2d3748'), yaxis=dict(gridcolor='#2d3748'))
        st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════
# PAGE 5 — DATA QUALITY
# ═══════════════════════════════════════════════
elif page == "🔍 Data Quality":
    st.markdown("# 🔍 Data Quality Report")
    st.caption("Phase 2 ETL Pipeline output — data validation and cleaning summary")
    st.markdown("---")

    # DQ metrics from Phase 2
    dq_data = {
        "Customers": {"Raw": 1005, "Valid": 965, "Rejected": 40, "Issues": "5 duplicates, 25 missing emails, 20 missing phones"},
        "Accounts":  {"Raw": 1500, "Valid": 1500, "Rejected": 0, "Issues": "None (clean)"},
        "Transactions": {"Raw": 10000, "Valid": 9990, "Rejected": 10, "Issues": "10 negative amount records"},
    }

    c1, c2, c3 = st.columns(3)
    total_raw = sum(v["Raw"] for v in dq_data.values())
    total_valid = sum(v["Valid"] for v in dq_data.values())
    total_rejected = sum(v["Rejected"] for v in dq_data.values())
    dq_score = round(total_valid / total_raw * 100, 2)

    with c1:
        st.metric("Total Raw Records", f"{total_raw:,}")
    with c2:
        st.metric("Valid Records", f"{total_valid:,}", delta=f"{dq_score}% quality score")
    with c3:
        st.metric("Rejected Records", f"{total_rejected:,}", delta_color="inverse", delta="Cleaned out")

    st.markdown("---")

    # DQ table
    st.markdown('<div class="section-header">📋 Breakdown by Entity</div>', unsafe_allow_html=True)
    dq_rows = []
    for entity, vals in dq_data.items():
        score = round(vals["Valid"] / vals["Raw"] * 100, 1)
        dq_rows.append({
            "Entity": entity,
            "Raw Records": vals["Raw"],
            "Valid Records": vals["Valid"],
            "Rejected": vals["Rejected"],
            "Quality Score": f"{score}%",
            "Issues Found": vals["Issues"]
        })
    st.dataframe(pd.DataFrame(dq_rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Visual
    st.markdown('<div class="section-header">📊 Valid vs Rejected by Entity</div>', unsafe_allow_html=True)
    rows = []
    for entity, vals in dq_data.items():
        rows.append({"Entity": entity, "Category": "Valid", "Count": vals["Valid"]})
        rows.append({"Entity": entity, "Category": "Rejected", "Count": vals["Rejected"]})
    dq_chart = pd.DataFrame(rows)
    fig = px.bar(dq_chart, x="Entity", y="Count", color="Category", barmode="group",
                 color_discrete_map={"Valid": "#16a34a", "Rejected": "#dc2626"}, text_auto=True)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#e2e8f0", margin=dict(t=10, b=10),
                      xaxis_title="", yaxis_title="Record Count")
    st.plotly_chart(fig, use_container_width=True)


