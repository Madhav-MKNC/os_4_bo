import os
import pandas as pd
import json
from validation import *

INPUT_DIR = "input"
OUTPUT_DIR = "outputs"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def csv_to_json(file_path):
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")


def process_files(files):
    """Process multiple CSV files and generate valid + invalid output CSVs."""
    merged_json = []

    # Merge and filter
    for file in files:
        data_json = csv_to_json(file)
        for entry in data_json:
            if pd.notna(entry.get("*Customer First Name")) and pd.notna(entry.get("*Customer Mobile")):
                merged_json.append(entry)

    series = {}

    # Assign fields
    for entry in merged_json:
        entry["*Order Id"] = get_order_id(entry, series)
        entry["*Customer Mobile"] = make_valid_ph_(entry["*Customer Mobile"])
        entry["Order Date as dd-mm-yyyy hh:MM"] = get_today()
        entry["*Master SKU"] = entry["*Product Name"]
        entry["*Partial COD (Yes/No)"] = "No"
        entry["Customer Alternate Mobile"] = make_valid_alternate_ph_num(
            entry["*Customer Mobile"], entry.get("Customer Alternate Mobile", "")
        )
        entry["*Shipping Address Line 1"] = make_valid_addr(entry["*Shipping Address Line 1"])

        key = entry["*Product Name"].lower()
        series[key] = series.get(key, 0) + 1

    invalid_entries = []
    valid_entries = []

    # Validate
    for entry in merged_json:
        if not correct_ph_num(entry["*Customer Mobile"]):
            invalid_entries.append(entry)
            continue
        if not correct_ph_num(entry["Customer Alternate Mobile"]):
            invalid_entries.append(entry)
            continue
        if not correct_pincode(entry["*Shipping Address Postcode"]):
            invalid_entries.append(entry)
            continue
        if len(str(entry["*Shipping Address Line 1"])) >= 180:
            invalid_entries.append(entry)
            continue

        valid_entries.append(entry)

    # Save valid CSV
    df_valid = pd.json_normalize(valid_entries)
    valid_file = os.path.join(OUTPUT_DIR, f"Order_Upload_Valid_{len(valid_entries)}.csv")
    df_valid.to_csv(valid_file, index=False)

    # Save invalid CSV if any
    invalid_file = None
    if len(invalid_entries):
        df_invalid = pd.json_normalize(invalid_entries)
        invalid_file = os.path.join(OUTPUT_DIR, f"Invalid_{len(invalid_entries)}.csv")
        df_invalid.to_csv(invalid_file, index=False)

    outputs = [valid_file]
    if invalid_file:
        outputs.append(invalid_file)

    return outputs
