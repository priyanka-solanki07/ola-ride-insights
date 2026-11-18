"""Ola Ride Insights - Streamlit app
Run:  streamlit run app.py
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

BASE = Path(__file__).parent
st.set_page_config(page_title="Ola Ride Insights", page_icon="🚖", layout="wide")


# ---------- data ----------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(BASE / "data" / "ola_cleaned.csv", parse_dates=["Date"])
    return df


@st.cache_resource
def get_connection():
    con = sqlite3.connect(":memory:", check_same_thread=False)
    load_data().assign(Date=lambda d: d["Date"].dt.strftime("%Y-%m-%d")).to_sql(
        "ola_rides", con, index=False
    )
    return con


@st.cache_data
def load_queries() -> list[tuple[str, str]]:
    """Parse sql/ola_queries.sql into (title, query) pairs."""
    text = (BASE / "sql" / "ola_queries.sql").read_text()
    out = []
    for block in text.split(";"):
        m = re.search(r"--\s*(Q\d+\..*)", block)
        if m and "SELECT" in block:
            q = "\n".join(l for l in block.splitlines() if not l.strip().startswith("--")).strip()
            out.append((m.group(1).strip(), q + ";"))
    return out


df = load_data()

# ---------- sidebar filters ----------
st.sidebar.title("🚖 Filters")
dmin, dmax = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
vehicles = st.sidebar.multiselect("Vehicle type", sorted(df["Vehicle_Type"].unique()),
                                  default=sorted(df["Vehicle_Type"].unique()))
statuses = st.sidebar.multiselect("Booking status", sorted(df["Booking_Status"].unique()),
                                  default=sorted(df["Booking_Status"].unique()))

f = df[df["Vehicle_Type"].isin(vehicles) & df["Booking_Status"].isin(statuses)]
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    f = f[(f["Date"].dt.date >= date_range[0]) & (f["Date"].dt.date <= date_range[1])]
succ = f[f["Booking_Status"] == "Success"]

st.title("Ola Ride Insights")
st.caption("July 2024 · Ride-sharing & mobility analytics")

# ---------- KPIs ----------
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total bookings", f"{len(f):,}")
k2.metric("Success rate", f"{(len(succ) / len(f) * 100 if len(f) else 0):.1f}%")
k3.metric("Revenue (successful)", f"₹{succ['Booking_Value'].sum():,.0f}")
k4.metric("Avg driver rating", f"{succ['Driver_Ratings'].mean():.2f}" if len(succ) else "-")
k5.metric("Avg customer rating", f"{succ['Customer_Rating'].mean():.2f}" if len(succ) else "-")

tabs = st.tabs(["Overall", "Vehicle Type", "Revenue", "Cancellation", "Ratings",
                "SQL Explorer", "Power BI"])

# ---------- Overall ----------
with tabs[0]:
    c1, c2 = st.columns(2)
    daily = f.groupby("Date").size().reset_index(name="Rides")
    c1.plotly_chart(px.line(daily, x="Date", y="Rides", title="Ride volume over time"),
                    width="stretch")
    status = f["Booking_Status"].value_counts().reset_index()
    status.columns = ["Status", "Count"]
    c2.plotly_chart(px.pie(status, names="Status", values="Count", hole=0.45,
                           title="Booking status breakdown"), width="stretch")
    hourly = f.groupby("Hour").size().reset_index(name="Rides")
    st.plotly_chart(px.bar(hourly, x="Hour", y="Rides", title="Demand by hour of day"),
                    width="stretch")

# ---------- Vehicle type ----------
with tabs[1]:
    v = f.groupby("Vehicle_Type").agg(
        Total_Booking_Value=("Booking_Value", "sum"),
        Avg_Distance=("Ride_Distance", "mean"),
        Total_Distance=("Ride_Distance", "sum"),
    ).reset_index()
    sv = succ.groupby("Vehicle_Type")["Booking_Value"].sum().rename("Success_Booking_Value")
    v = v.merge(sv, on="Vehicle_Type", how="left").round(2)
    st.dataframe(v, width="stretch", hide_index=True)
    top5 = v.nlargest(5, "Total_Distance")
    st.plotly_chart(px.bar(top5, x="Vehicle_Type", y="Total_Distance",
                           title="Top 5 vehicle types by ride distance"), width="stretch")

# ---------- Revenue ----------
with tabs[2]:
    c1, c2 = st.columns(2)
    pay = succ.groupby("Payment_Method")["Booking_Value"].sum().reset_index()
    c1.plotly_chart(px.pie(pay, names="Payment_Method", values="Booking_Value",
                           title="Revenue by payment method"), width="stretch")
    cust = (succ.groupby("Customer_ID")["Booking_Value"].sum()
            .nlargest(5).reset_index())
    c2.plotly_chart(px.bar(cust, x="Customer_ID", y="Booking_Value",
                           title="Top 5 customers by booking value"), width="stretch")
    dist = succ.groupby("Date")["Ride_Distance"].sum().reset_index()
    st.plotly_chart(px.line(dist, x="Date", y="Ride_Distance",
                            title="Ride distance per day"), width="stretch")

# ---------- Cancellation ----------
with tabs[3]:
    c1, c2 = st.columns(2)
    cc = f[f["Canceled_Rides_by_Customer"] != "Not Applicable"]["Canceled_Rides_by_Customer"].value_counts().reset_index()
    cc.columns = ["Reason", "Count"]
    c1.plotly_chart(px.bar(cc, x="Count", y="Reason", orientation="h",
                           title="Cancelled by customers - reasons"), width="stretch")
    cd = f[f["Canceled_Rides_by_Driver"] != "Not Applicable"]["Canceled_Rides_by_Driver"].value_counts().reset_index()
    cd.columns = ["Reason", "Count"]
    c2.plotly_chart(px.bar(cd, x="Count", y="Reason", orientation="h",
                           title="Cancelled by drivers - reasons"), width="stretch")

# ---------- Ratings ----------
with tabs[4]:
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.histogram(succ, x="Driver_Ratings", nbins=20,
                                 title="Driver ratings distribution"), width="stretch")
    c2.plotly_chart(px.histogram(succ, x="Customer_Rating", nbins=20,
                                 title="Customer ratings distribution"), width="stretch")
    avg = succ.groupby("Vehicle_Type")[["Driver_Ratings", "Customer_Rating"]].mean().round(2).reset_index()
    st.plotly_chart(px.bar(avg.melt("Vehicle_Type"), x="Vehicle_Type", y="value", color="variable",
                           barmode="group", title="Customer vs driver ratings by vehicle type"),
                    width="stretch")

# ---------- SQL explorer ----------
with tabs[5]:
    st.subheader("Project SQL questions")
    queries = load_queries()
    choice = st.selectbox("Pick a query", [t for t, _ in queries])
    sql = dict(queries)[choice]
    st.code(sql, language="sql")
    res = pd.read_sql(sql, get_connection())
    st.write(f"{len(res):,} rows")
    st.dataframe(res.head(1000), width="stretch", hide_index=True)

    st.subheader("Write your own query")
    custom = st.text_area("SELECT ... FROM ola_rides", "SELECT Vehicle_Type, COUNT(*) AS rides FROM ola_rides GROUP BY Vehicle_Type;")
    if st.button("Run"):
        if custom.strip().lower().startswith("select"):
            try:
                st.dataframe(pd.read_sql(custom, get_connection()), width="stretch")
            except Exception as e:
                st.error(e)
        else:
            st.warning("Only SELECT queries are allowed.")

# ---------- Power BI ----------
with tabs[6]:
    st.subheader("Embedded Power BI dashboard")
    url = st.text_input("Paste your Power BI 'Publish to web' embed URL")
    if url:
        components.iframe(url, height=650, scrolling=True)
    else:
        st.info("Power BI Service > Publish to web > copy the embed link, then paste it above.")
