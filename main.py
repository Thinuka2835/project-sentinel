import osimport jsonimport csvfrom data_integration import synchronize_datafrom challenge_detection import (    detect_scan_avoidance, detect_barcode_switching, detect_system_crashes,    detect_weight_discrepancies, detect_long_queues, detect_inventory_discrepancies,    detect_long_wait_times)DATA_INPUT_DIR = os.path.join('data', 'input')def read_jsonl(filepath, limit=5):    """Read up to `limit` JSON objects from a .jsonl file."""    results = []    with open(filepath, 'r', encoding='utf-8') as f:        for i, line in enumerate(f):            if i >= limit:                break            try:                results.append(json.loads(line))            except json.JSONDecodeError:                print(f"Malformed JSON in {filepath}: {line.strip()}")    return resultsdef read_csv(filepath):    """Read a CSV file into a list of dicts."""    with open(filepath, 'r', encoding='utf-8') as f:        reader = csv.DictReader(f)        return list(reader)def main():    print("Loading and synchronizing data...")    data = synchronize_data()    rfid = data['rfid']    queue = data['queue']    pos = data['pos']    recog = data['recog']    inventory = data['inventory']    products = data['products']    customers = data['customers']    print("\n--- Challenge Detection Summary ---")    scan_avoidance = detect_scan_avoidance(rfid, pos)    print(f"Scan avoidance incidents: {scan_avoidance}")

    barcode_switching = detect_barcode_switching(pos, recog)
    print(f"Barcode switching incidents: {barcode_switching}")

    system_crashes = detect_system_crashes(pos)
    print(f"System crashes or scanning errors: {system_crashes}")

    weight_discrepancies = detect_weight_discrepancies(pos, products)
    print(f"Weight discrepancies: {weight_discrepancies}")

    long_queues = detect_long_queues(queue)
    print(f"Long queue situations: {long_queues}")

    inventory_discrepancies = detect_inventory_discrepancies(inventory, pos)
    print(f"Inventory discrepancies: {inventory_discrepancies}")

    long_wait_times = detect_long_wait_times(queue)
    print(f"Extended customer wait times: {long_wait_times}")

    print("Reading JSONL files from data/input:")
    for fname in os.listdir(DATA_INPUT_DIR):
        if fname.endswith('.jsonl'):
            path = os.path.join(DATA_INPUT_DIR, fname)
            print(f"\n{fname}:")
            events = read_jsonl(path)
            for i, event in enumerate(events):
                print(f"  Event {i+1}: {event}")

    print("\nReading CSV lookup tables:")
    for fname in os.listdir(DATA_INPUT_DIR):
        if fname.endswith('.csv'):
            path = os.path.join(DATA_INPUT_DIR, fname)
            rows = read_csv(path)
            print(f"\n{fname}: {len(rows)} rows loaded")
            print(f"  First row: {rows[0] if rows else 'No data'}")

if __name__ == "__main__":
    main()