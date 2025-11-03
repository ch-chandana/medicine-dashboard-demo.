import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="🏥 Medicine Monitoring (Demo)", page_icon="💊", layout="wide")

st.title("🏥 Intelligent Medicine Refill & Expiry Alert System (Cloud Demo)")
st.markdown("Upload your hospital’s medicine data to visualize alerts instantly — no Kafka required.")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload your medicines CSV file", type=["csv"])

if uploaded_file:
    # Read data
    df = pd.read_csv(uploaded_file)

    # Add timestamp
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------------- ALERT LOGIC ----------------
    alerts = []
    for _, row in df.iterrows():
        # Low Stock
        if row["quantity"] < row["min_threshold"]:
            alerts.append({
                "name": row["name"],
                "batch": row["batch"],
                "alert_type": "LOW_STOCK",
                "alert_message": f"LOW STOCK: {row['name']} has only {row['quantity']} units (min: {row['min_threshold']})",
                "priority": "HIGH",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        # Expiry Check
        if "2024-03" in row["expiry_date"] or "2024-04" in row["expiry_date"]:
            alerts.append({
                "name": row["name"],
                "batch": row["batch"],
                "alert_type": "EXPIRING_SOON",
                "alert_message": f"EXPIRING: {row['name']} batch {row['batch']} expires on {row['expiry_date']}",
                "priority": "MEDIUM",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    # ---------------- DISPLAY RESULTS ----------------
    if not alerts:
        st.success("✅ All medicines are healthy and within safe stock levels.")
    else:
        alert_df = pd.DataFrame(alerts)

        # ---- METRICS ----
        col1, col2, col3 = st.columns(3)
        col1.metric("💊 Total Alerts", len(alert_df))
        col2.metric("🔴 Low Stock", (alert_df["alert_type"] == "LOW_STOCK").sum())
        col3.metric("🟡 Expiring Soon", (alert_df["alert_type"] == "EXPIRING_SOON").sum())

        st.markdown("---")

        # ---- ALERT TABLE & CHARTS ----
        with st.container():
            st.subheader("📢 Current Alerts Overview")
            st.dataframe(
                alert_df[["timestamp", "name", "alert_type", "alert_message", "priority"]],
                use_container_width=True,
                hide_index=True
            )

            chart_col1, chart_col2 = st.columns([2, 1])

            with chart_col1:
                st.subheader("📊 Alerts by Medicine")
                st.bar_chart(alert_df["name"].value_counts())

            with chart_col2:
                st.subheader("🧭 Alert Type Share")
                type_counts = alert_df["alert_type"].value_counts()
                st.pyplot(type_counts.plot.pie(autopct="%1.0f%%", ylabel="", figsize=(3,3)).get_figure())

        # ---- TOAST NOTIFICATIONS ----
        for _, alert in alert_df.iterrows():
            if alert["priority"] == "HIGH":
                st.toast(f"🚨 {alert['alert_message']}", icon="🚨")
            else:
                st.toast(f"⚠️ {alert['alert_message']}", icon="⚠️")

else:
    st.info("📂 Please upload a CSV file to begin monitoring.")

st.markdown("---")
st.caption("🌐 Cloud Demo Version — Upload CSV to simulate hospital monitoring in real-time.")
