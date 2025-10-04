import os
import streamlit as st
import pandas as pd
from data_integration import synchronize_data
from challenge_detection import (
    detect_scan_avoidance, detect_barcode_switching, detect_system_crashes,
    detect_weight_discrepancies, detect_long_queues, detect_inventory_discrepancies,
    detect_long_wait_times
)

st.set_page_config(page_title="Store Status Dashboard", layout="wide")
st.title("🛒 Real-Time Store Status Overview")

# Load and synchronize all data
data = synchronize_data()
rfid = data['rfid']
queue = data['queue']
pos = data['pos']
recog = data['recog']
inventory = data['inventory']
products = data['products']
customers = data['customers']

# --- Inventory Status ---
st.header("Inventory Status")
if not inventory.empty:
    latest_inventory = inventory.iloc[-1]['data']
    inventory_table = pd.DataFrame(list(latest_inventory.items()), columns=['SKU', 'On Hand'])
    inventory_table = inventory_table.merge(products[['SKU', 'product_name']], on='SKU', how='left')
    st.dataframe(inventory_table)
else:
    st.info("No inventory data available.")

# --- Customer Flow Visualization ---
st.header("Customer Flow")
if not queue.empty:
    queue['customer_count'] = queue['data'].apply(lambda d: d['customer_count'])
    queue['timestamp'] = pd.to_datetime(queue['timestamp'])
    st.line_chart(queue.set_index('timestamp')['customer_count'])
else:
    st.info("No queue monitoring data available.")

# --- Resource Allocation ---
st.header("Resource Allocation")
if not pos.empty:
    pos['station'] = pos['station_id']
    station_counts = pos['station'].value_counts().sort_index()
    st.bar_chart(station_counts)
else:
    st.info("No POS transaction data available.")

# --- Anomalies & Alerts ---
st.header("Anomalies & Alerts")
alerts = []

scan_avoidance = detect_scan_avoidance(rfid, pos)
if scan_avoidance:
    alerts.append(("High", f"Scan avoidance incidents detected: {scan_avoidance}"))

barcode_switching = detect_barcode_switching(pos, recog)
if barcode_switching:
    alerts.append(("High", f"Barcode switching incidents detected: {barcode_switching}"))

system_crashes = detect_system_crashes(pos)
if not system_crashes.empty:
    alerts.append(("High", f"System crashes or scanning errors: {len(system_crashes)} incidents"))

weight_discrepancies = detect_weight_discrepancies(pos, products)
if weight_discrepancies:
    alerts.append(("Medium", f"Weight discrepancies: {weight_discrepancies}"))

long_queues = detect_long_queues(queue)
if not long_queues.empty:
    alerts.append(("Medium", f"Long queue situations: {len(long_queues)} times"))

inventory_discrepancies = detect_inventory_discrepancies(inventory, pos)
if inventory_discrepancies:
    alerts.append(("Medium", f"Inventory discrepancies: {inventory_discrepancies}"))

long_wait_times = detect_long_wait_times(queue)
if not long_wait_times.empty:
    alerts.append(("Low", f"Extended customer wait times: {len(long_wait_times)} times"))

if not alerts:
    st.success("No anomalies detected.")
else:
    for level, msg in alerts:
        if level == "High":
            st.error(msg)
        elif level == "Medium":
            st.warning(msg)
        else:
            st.info(msg)

st.caption("Dashboard auto-refreshes on reload. For real-time, set up Streamlit auto-refresh or polling.")


