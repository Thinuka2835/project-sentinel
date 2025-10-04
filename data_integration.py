import os
import json
import pandas as pd

DATA_INPUT_DIR = os.path.join('data', 'input')

def load_jsonl(filename):
    path = os.path.join(DATA_INPUT_DIR, filename)
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except Exception:
                continue
    return pd.DataFrame(data)

def load_csv(filename):
    path = os.path.join(DATA_INPUT_DIR, filename)
    return pd.read_csv(path)

def synchronize_data():
    return {
        "rfid": load_jsonl('rfid_readings.jsonl'),
        "queue": load_jsonl('queue_monitoring.jsonl'),
        "pos": load_jsonl('pos_transactions.jsonl'),
        "recog": load_jsonl('product_recognition.jsonl'),
        "inventory": load_jsonl('inventory_snapshots.jsonl'),
        "products": load_csv('products_list.csv'),
        "customers": load_csv('customer_data.csv')
    }