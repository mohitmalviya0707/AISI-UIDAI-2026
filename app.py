

import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="AISI Dashboard", layout="wide")

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.title("📊 Aadhaar Inclusion Stress Index (AISI) – District Dashboard")
st.write("UIDAI Data Hackathon 2026 | Developed by **Mohit Malviya **")

# ---------------------------------------------------
# AUTO-DETECT CSV FILE
# ---------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_files = glob.glob(os.path.join(PROJECT_DIR, "**", "aisi_district_results.csv"), recursive=True)

if not csv_files:
    st.error("❌ CSV Not Found! Place `aisi_district_results.csv` anywhere in project folder.")
    st.stop()

csv_path = csv_files[0]
st.success(f"✅ CSV Loaded from: {csv_path}")

df = pd.read_csv(csv_path)

# ---------------------------------------------------
# PREVIEW
# ---------------------------------------------------
st.subheader("📁 Dataset Preview")
st.dataframe(df.head())

# ---------------------------------------------------
# FILTERS (Sidebar)
# ---------------------------------------------------
st.sidebar.header("🔍 Filters")

state_filter = st.sidebar.selectbox(
    "Select State",
    ["All"] + sorted(df["state"].astype(str).unique().tolist())
)

stress_filter = st.sidebar.selectbox(
    "Select AISI Level",
    ["All"] + sorted(df["AISI_level"].astype(str).unique().tolist())
)

filtered_df = df.copy()

if state_filter != "All":
    filtered_df = filtered_df[filtered_df["state"] == state_filter]

if stress_filter != "All":
    filtered_df = filtered_df[filtered_df["AISI_level"] == stress_filter]

# ---------------------------------------------------
# FILTERED RESULTS
# ---------------------------------------------------
st.subheader("🎯 Filtered Results")
st.dataframe(filtered_df)

# ---------------------------------------------------
# KEY METRICS
# ---------------------------------------------------
st.subheader("📌 Key Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Total Districts", len(filtered_df))
col2.metric("High Stress Districts", len(filtered_df[filtered_df["AISI_level"] == "High"]))
col3.metric("Avg Child Ratio", round(filtered_df["child_ratio"].mean(), 2))

# ---------------------------------------------------
# STATE SUMMARY
# ---------------------------------------------------
st.subheader("🧭 State Summary Insights")

if state_filter != "All":
    state_data = df[df["state"] == state_filter]

    total_dist = len(state_data)
    high_cnt = len(state_data[state_data["AISI_level"] == "High"])
    low_cnt = len(state_data[state_data["AISI_level"] == "Low"])

    st.markdown(f"""
    ### 📍 **State: {state_filter}**
    - Total Districts: **{total_dist}**
    - High Stress Districts: **{high_cnt}**
    - Low Stress Districts: **{low_cnt}**
    """)

    if high_cnt > 0:
        worst = state_data[state_data["AISI_level"] == "High"].nlargest(1, "child_ratio")
        st.markdown(f"""
        ### 🚨 Worst District:
        **{worst.iloc[0]['district']}**  
        Child Ratio: **{worst.iloc[0]['child_ratio']:.2f}**
        """)

# ---------------------------------------------------
# PIE CHART – AISI LEVEL DISTRIBUTION
# ---------------------------------------------------
st.subheader("📈 AISI Level Distribution (Pie Chart)")

levels = df["AISI_level"].value_counts()

fig_pie = go.Figure(data=[go.Pie(
    labels=levels.index,
    values=levels.values,
    hole=0.4
)])
fig_pie.update_layout(width=600, height=400)
st.plotly_chart(fig_pie)

# ---------------------------------------------------
# HIGH STRESS DISTRICTS BAR CHART
# ---------------------------------------------------
st.subheader("🚨 Top 15 High-Stress Districts (Child Ratio)")

high_df = filtered_df[filtered_df["AISI_level"] == "High"]

if len(high_df) == 0:
    st.info("No high-stress districts in selected filters.")
else:
    top15 = high_df.nlargest(15, "child_ratio")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top15["district"], top15["child_ratio"], color="red")
    ax.set_xlabel("Child Ratio")
    ax.set_title("Top High-Stress Districts")
    plt.tight_layout()

    st.pyplot(fig)

# ---------------------------------------------------
# DISTRICT COMPARISON CHART
# ---------------------------------------------------
st.subheader("🏆 District Comparison – Highest Child Ratio (Top 20)")

sorted_df = filtered_df.sort_values("child_ratio", ascending=False).head(20)

fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.bar(sorted_df["district"], sorted_df["child_ratio"], color="orange")
plt.xticks(rotation=80)
st.pyplot(fig2)

# ---------------------------------------------------
# PROBLEM DIAGNOSIS & SOLUTIONS
# ---------------------------------------------------
st.subheader("🛠 Problem Diagnosis & Recommended Solutions")

if state_filter != "All":
    state_data = df[df["state"] == state_filter]
    high_d = state_data[state_data["AISI_level"] == "High"]

    if len(high_d) == 0:
        st.success("✔ State performing well. No high-stress districts!")
    else:
        st.warning("High-Stress Districts Identified:")
        st.dataframe(high_d[["district", "child_ratio"]])

        st.markdown("""
        ### ✅ Recommended Fixes:
        - Increase Aadhaar enrollment camps for 0–5 age group  
        - Improve operator training in low-performing districts  
        - Deploy temporary mobile enrollment units  
        - Add more Aadhaar centers in rural belts  
        - Strengthen biometric quality through better devices  
        """)

# ---------------------------------------------------
# DOWNLOAD BUTTON
# ---------------------------------------------------
st.subheader("⬇️ Download Filtered Data")

st.download_button(
    label="Download CSV",
    data=filtered_df.to_csv(index=False),
    file_name="AISI_filtered_districts.csv",
    mime="text/csv"
)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")



