import os
import streamlit as st
import pandas as pd
import json
from data_integration import synchronize_data
from challenge_detection import (
    detect_scan_avoidance, detect_barcode_switching, detect_system_crashes,
    detect_weight_discrepancies, detect_long_queues, detect_inventory_discrepancies,
    detect_long_wait_times
)

DATA_INPUT_DIR = os.path.join('data', 'input')

def load_jsonl(filename, limit=1000):
    path = os.path.join(DATA_INPUT_DIR, filename)
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            try:
                data.append(json.loads(line))
            except Exception:
                continue
    return pd.DataFrame(data)

def load_csv(filename):
    path = os.path.join(DATA_INPUT_DIR, filename)
    return pd.read_csv(path)

st.set_page_config(page_title="Store Status Dashboard", layout="wide")
st.title("🛒 Real-Time Store Status Overview")

# Inventory Status
st.header("Inventory Status")
inventory_df = load_jsonl('inventory_snapshots.jsonl', limit=1)
if not inventory_df.empty:
    inventory = inventory_df.iloc[0]['data']
    inventory_table = pd.DataFrame(list(inventory.items()), columns=['SKU', 'On Hand'])
    st.dataframe(inventory_table)
else:
    st.info("No inventory data available.")

# Customer Flow Visualization
st.header("Customer Flow")
queue_df = load_jsonl('queue_monitoring.jsonl')
if not queue_df.empty:
    st.line_chart(queue_df[['timestamp', 'data']].apply(lambda row: row['data']['customer_count'], axis=1))
else:
    st.info("No queue monitoring data available.")

# Resource Allocation (POS, Staff, etc.)
st.header("Resource Allocation")
pos_df = load_jsonl('pos_transactions.jsonl')
if not pos_df.empty:
    pos_counts = pos_df['station_id'].value_counts()
    st.bar_chart(pos_counts)
else:
    st.info("No POS transaction data available.")

# Anomalies & Alerts
st.header("Anomalies & Alerts")
alerts = []
if not queue_df.empty:
    for _, row in queue_df.iterrows():
        if row['data']['customer_count'] > 10:
            alerts.append(("High queue at station", row['station_id'], "High"))
        if row['data']['average_dwell_time'] > 300:
            alerts.append(("Long dwell time", row['station_id'], "Medium"))
if not alerts:
    st.success("No anomalies detected.")
else:
    for alert in alerts:
        if alert[2] == "High":
            st.error(f"{alert[0]}: {alert[1]}")
        else:
            st.warning(f"{alert[0]}: {alert[1]}")

# Data Synchronization and Challenge Detection
data = synchronize_data()
rfid = data['rfid']
queue = data['queue']
pos = data['pos']
recog = data['recog']
inventory = data['inventory']
products = data['products']
customers = data['customers']

# Example: Show scan avoidance incidents
scan_avoidance = detect_scan_avoidance(rfid, pos)
if scan_avoidance:
    st.error(f"Scan avoidance incidents detected: {scan_avoidance}")
else:
    st.success("No scan avoidance incidents detected.")

# Repeat for other challenge detections and visualize as needed

st.caption("Data updates on page refresh. For real-time, set up auto-refresh or polling.")


