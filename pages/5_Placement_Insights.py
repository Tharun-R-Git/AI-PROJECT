import streamlit as st

# --- Authentication Check ---
# Stop the page from loading if the user is not logged in
if not st.session_state.get("logged_in"):
    st.error("Please log in from the 🏠 Home page to use this feature.")
    st.stop()

# Block admin access to student features
if st.session_state.get("role") == "admin":
    st.error("Access Denied: This feature is for students only. Admins cannot access student features.")
    st.stop()


# app.py
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import numpy as np


st.title("CDC Assistant — Advanced Placement Analytics Dashboard")
st.caption("Interactive analytics for placement trends, package statistics, and branch performance at VIT.")

# -----------------------------------------------------------
# LOAD DATABASE
# -----------------------------------------------------------
@st.cache_data
def load_data(db_path="data.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM companies", conn)
    conn.close()

    # Normalize columns
    df.columns = (
        df.columns.str.strip()
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.upper()
    )
    return df

df = load_data()

# -----------------------------------------------------------
# FILTERS
# -----------------------------------------------------------
st.sidebar.header("Filters")

months = st.sidebar.multiselect(
    "Select Month(s):",
    options=df["MONTH"].unique(),
    default=df["MONTH"].unique()
)

min_ctc, max_ctc = st.sidebar.slider(
    "Average CTC Range (LPA):",
    float(df["AVERAGE_CTC_LPA"].min()),
    float(df["AVERAGE_CTC_LPA"].max()),
    (float(df["AVERAGE_CTC_LPA"].min()), float(df["AVERAGE_CTC_LPA"].max()))
)

filtered_df = df[
    (df["MONTH"].isin(months)) &
    (df["AVERAGE_CTC_LPA"].between(min_ctc, max_ctc))
]

branch_columns = ["BBS", "BCE", "BCI", "BCT", "BDS", "BEC", "BEE", "BIT", "BKT"]
filtered_df = filtered_df.copy()
filtered_df["TOTAL_PLACED"] = filtered_df[branch_columns].sum(axis=1)

# -----------------------------------------------------------
# KEY METRICS
# -----------------------------------------------------------
st.subheader("Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

avg_ctc = round(filtered_df["AVERAGE_CTC_LPA"].mean(), 2)
median_ctc = round(filtered_df["AVERAGE_CTC_LPA"].median(), 2)
max_ctc = round(filtered_df["AVERAGE_CTC_LPA"].max(), 2)
total_students = int(filtered_df["TOTAL_PLACED"].sum())
unique_companies = filtered_df["COMPANY"].nunique()

col1.metric("Average Package (LPA)", avg_ctc)
col2.metric("Median Package (LPA)", median_ctc)
col3.metric("Highest Package (LPA)", max_ctc)
col4.metric("Total Students Placed", total_students)
col5.metric("Companies Visited", unique_companies)

st.divider()

# -----------------------------------------------------------
# VISUALIZATIONS
# -----------------------------------------------------------

# Average CTC by Month
st.subheader("Average Package by Month")
month_ctc = filtered_df.groupby("MONTH")["AVERAGE_CTC_LPA"].mean().reset_index()
fig1 = px.bar(month_ctc, x="MONTH", y="AVERAGE_CTC_LPA", color="MONTH", text_auto=True,
              title="Average Package Trend by Month")
st.plotly_chart(fig1, use_container_width=True)

# Branch-wise placement totals
st.subheader("Placement Distribution by Branch")
branch_totals = filtered_df[branch_columns].sum().reset_index()
branch_totals.columns = ["Branch", "Students_Placed"]
fig2 = px.bar(branch_totals, x="Branch", y="Students_Placed", color="Branch",
              title="Total Placements by Branch", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Branch-wise statistics
st.subheader("Branch-wise Statistics")
branch_stats = []
for branch in branch_columns:
    sub_df = filtered_df[filtered_df[branch] > 0]
    avg_ctc_b = sub_df["AVERAGE_CTC_LPA"].mean() if not sub_df.empty else np.nan
    median_ctc_b = sub_df["AVERAGE_CTC_LPA"].median() if not sub_df.empty else np.nan
    total_b = sub_df[branch].sum()
    branch_stats.append({
        "Branch": branch,
        "Average_Package_LPA": round(avg_ctc_b, 2) if not np.isnan(avg_ctc_b) else 0,
        "Median_Package_LPA": round(median_ctc_b, 2) if not np.isnan(median_ctc_b) else 0,
        "Total_Students_Placed": int(total_b)
    })

branch_stats_df = pd.DataFrame(branch_stats).sort_values(by="Average_Package_LPA", ascending=False)
st.dataframe(branch_stats_df, use_container_width=True)

# Top Paying Companies
st.subheader("Top Paying Companies")
top_companies = (
    filtered_df.groupby("COMPANY")["AVERAGE_CTC_LPA"]
    .mean()
    .reset_index()
    .sort_values(by="AVERAGE_CTC_LPA", ascending=False)
    .head(10)
)
fig3 = px.bar(top_companies, x="AVERAGE_CTC_LPA", y="COMPANY", orientation="h", color="AVERAGE_CTC_LPA",
              title="Top 10 Highest Average Packages", text_auto=True)
st.plotly_chart(fig3, use_container_width=True)

# Most Hiring Companies
st.subheader("Top Companies by Number of Placements")
most_hiring = (
    filtered_df.groupby("COMPANY")["TOTAL_PLACED"]
    .sum()
    .reset_index()
    .sort_values(by="TOTAL_PLACED", ascending=False)
    .head(10)
)
fig4 = px.bar(most_hiring, x="TOTAL_PLACED", y="COMPANY", orientation="h", color="TOTAL_PLACED",
              title="Top 10 Companies by Students Placed", text_auto=True)
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------------------------------
# COMPANY-LEVEL ANALYTICS
# -----------------------------------------------------------
st.subheader("Company Level Analytics")

selected_company = st.selectbox("Select a Company:", options=sorted(filtered_df["COMPANY"].unique()))
if selected_company:
    comp_data = filtered_df[filtered_df["COMPANY"] == selected_company]
    st.write(f"Summary for {selected_company}:")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Package (LPA)", round(comp_data["AVERAGE_CTC_LPA"].mean(), 2))
    col2.metric("Median Package (LPA)", round(comp_data["AVERAGE_CTC_LPA"].median(), 2))
    col3.metric("Total Students Placed", int(comp_data["TOTAL_PLACED"].sum()))

    branch_split = comp_data[branch_columns].sum().reset_index()
    branch_split.columns = ["Branch", "Students_Placed"]
    fig5 = px.bar(branch_split, x="Branch", y="Students_Placed", color="Branch",
                  title=f"Branch-wise Placement Split for {selected_company}", text_auto=True)
    st.plotly_chart(fig5, use_container_width=True)

# -----------------------------------------------------------
# RAW DATA
# -----------------------------------------------------------
st.divider()
st.subheader("Filtered Data")
st.dataframe(filtered_df, use_container_width=True)
st.caption("Use the sidebar filters to explore placement patterns by month and CTC range.")
