import os
import pandas as pd
import json
import chardet

from configs import INPUT_FOLDER, OUTPUT_FOLDER
from processing_and_pre_processing.validation import *


def csv_to_json(file_name):
    """Convert a CSV file into JSON-like Python dictionaries with safe encoding detection."""
    file_path = os.path.join(INPUT_FOLDER, file_name)

    # Detect encoding safely
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(100000))
    encoding = result.get('encoding', 'utf-8')
    print(f"Detected encoding for {file_name}: {encoding}")

    # Try reading CSV with multiple fallbacks
    try:
        df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
    except UnicodeDecodeError:
        print(f"⚠️ Failed with {encoding}, trying 'utf-8-sig'...")
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
        except UnicodeDecodeError:
            print(f"⚠️ Failed with 'utf-8-sig', trying 'latin1'...")
            df = pd.read_csv(file_path, encoding='latin1', low_memory=False)

    return df.to_dict(orient="records")


def process_files(files):
    """
    Process all CSV files, clean and validate records,
    and output valid + invalid CSVs.
    """
    merged_json = []
    failed_files = []
    mknc_outputs = []

    # Step 1: Merge and filter data
    for f in files:
        try:
            data_json = csv_to_json(f)
            for entry in data_json:
                if pd.notna(entry.get("*Customer First Name")) and pd.notna(entry.get("*Customer Mobile")):
                    entry["FILENAME, INDEX, ROW"] = f"{f}, {data_json.index(entry) - 2}"
                    merged_json.append(entry)
        except Exception as e:
            print(f"❌ Failed to process {f}: {e}")
            failed_files.append(f)

    # Save any failed files list
    if failed_files:
        failed_files_output_file_path = os.path.join(OUTPUT_FOLDER, "failed_files.txt")
        with open(failed_files_output_file_path, 'w', encoding='utf-8') as file:
            file.write("\n".join(failed_files))
        mknc_outputs.append(failed_files_output_file_path)

    series = {}
    merged_json_valid_entries = []
    invalid_entries = []

    # Step 2: Assign computed fields and validate during assignment
    for it, entry in enumerate(merged_json):
        row_mknc = ""
        try:
            row_mknc = "*Order Id"
            entry[row_mknc] = get_order_id(entry, series)
            
            row_mknc = "*Customer Mobile"
            entry[row_mknc] = make_valid_ph_(entry["*Customer Mobile"])

            row_mknc = "Order Date as dd-mm-yyyy hh:MM"
            entry[row_mknc] = get_today()

            row_mknc = "*Master SKU"
            entry[row_mknc] = entry["*Product Name"]

            row_mknc = "*Partial COD (Yes/No)"
            entry[row_mknc] = "No"

            row_mknc = "Customer Alternate Mobile"
            entry[row_mknc] = make_valid_alternate_ph_num(
                entry["*Customer Mobile"],
                entry.get("Customer Alternate Mobile", "")
            )

            row_mknc = "*Shipping Address Line 1"
            entry[row_mknc] = make_valid_addr(entry["*Shipping Address Line 1"])

            key = entry["*Product Name"].lower()
            series[key] = series.get(key, 0) + 1

            merged_json_valid_entries.append(entry)

        except Exception as e:
            print(f"\n\n⚠️ INVALID ENTRY [{it}] — {entry.get('*Product Name')}\nReason: {e}\n")
            entry["FILENAME, INDEX, ROW"] = entry["FILENAME, INDEX, ROW"] + f", [{row_mknc}]"
            invalid_entries.append(entry)

    # Step 3: Validation of entries
    for entry in merged_json_valid_entries[:]:
        if not correct_ph_num(entry["*Customer Mobile"]):
            print("❌ Invalid primary phone")
            entry["FILENAME, INDEX, ROW"] = entry["FILENAME, INDEX, ROW"] + f", [*Customer Mobile]"
            invalid_entries.append(entry)
            merged_json_valid_entries.remove(entry)
            continue

        if not correct_ph_num(entry["Customer Alternate Mobile"]):
            print("❌ Invalid alternate phone")
            entry["FILENAME, INDEX, ROW"] = entry["FILENAME, INDEX, ROW"] + f", [Customer Alternate Mobile]"
            invalid_entries.append(entry)
            merged_json_valid_entries.remove(entry)
            continue

        if not correct_pincode(entry["*Shipping Address Postcode"]):
            print("❌ Invalid postcode")
            entry["FILENAME, INDEX, ROW"] = entry["FILENAME, INDEX, ROW"] + f", [*Shipping Address Postcode]"
            invalid_entries.append(entry)
            merged_json_valid_entries.remove(entry)
            continue

        if len(str(entry["*Shipping Address Line 1"])) >= 180:
            print("❌ Address too long")
            entry["FILENAME, INDEX, ROW"] = entry["FILENAME, INDEX, ROW"] + f", [*Shipping Address Line 1]"
            invalid_entries.append(entry)
            merged_json_valid_entries.remove(entry)
            continue

    # Step 4: Save valid CSV
    df_valid = pd.json_normalize(merged_json_valid_entries)
    df_valid = df_valid[order]
    valid_file = os.path.join(OUTPUT_FOLDER, f"Order_Upload_Valid_{len(merged_json_valid_entries)}.csv")
    df_valid.to_csv(valid_file, index=False)
    print(f"✅ Saved valid file: {valid_file}")
    mknc_outputs.append(valid_file)

    # Step 5: Save invalid CSV (if any)
    if len(invalid_entries):
        df_invalid = pd.json_normalize(invalid_entries)
        cols = order + ["FILENAME, INDEX, ROW"] if "FILENAME, INDEX, ROW" in df_invalid.columns else order
        df_invalid = df_invalid[cols]
        invalid_file = os.path.join(OUTPUT_FOLDER, f"Invalid_{len(invalid_entries)}.csv")
        df_invalid.to_csv(invalid_file, index=False)
        print(f"⚠️ Saved invalid file: {invalid_file}")
        mknc_outputs.append(invalid_file)

    # Step 6: Return output paths
    return mknc_outputs
