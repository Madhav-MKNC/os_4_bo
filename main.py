import pandas as pd
import json
import os
import chardet

from validation import *

# Directories
INPUT_DIR = "input"
OUTPUT_DIR = "outputs"
# MERGED_DIR = "merged"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs(MERGED_DIR, exist_ok=True)

# Get CSV files
files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".csv")]

# # Convert CSV to JSON
# def csv_to_json(file_name):
#     file_path = os.path.join(INPUT_DIR, file_name)
#     try:
#         df = pd.read_csv(file_path, encoding='utf-8')
#     except UnicodeDecodeError:
#         # Fallback if UTF-8 fails
#         df = pd.read_csv(file_path, encoding='latin1')
#     return df.to_dict(orient="records")


def csv_to_json(file_name):
    file_path = os.path.join(INPUT_DIR, file_name)
    
    # Detect encoding safely
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(100000))
    encoding = result.get('encoding', 'utf-8')
    print(f"Detected encoding for {file_name}: {encoding}")

    # Try reading with detected encoding; fallback to UTF-8 and Latin-1 if it fails
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


# Merge and filter data
merged_json = []
for f in files:
    try:
        data_json = csv_to_json(f)
        for entry in data_json:
            if pd.notna(entry.get("*Customer First Name")) and pd.notna(entry.get("*Customer Mobile")):
                entry["FILENAME, INDEX"] = f"{f}, {data_json.index(entry) - 2}"
                merged_json.append(entry)
    except:
        with open("failed_files.txt", 'w', encoding='utf-8') as file:
            file.write(f"{f}\n\n")

# # Save merged JSON
# with open(os.path.join(MERGED_DIR, "merged.json"), 'w', encoding='utf-8') as file:
#     json.dump(merged_json, file, ensure_ascii=False, indent=4)



series = {}
merged_json_valid_entries = []
invalid_entries = []


# assign order ids
for it, entry in enumerate(merged_json):
    # print(it, entry["*Product Name"].strip().split(" "))
    try:
        entry["*Order Id"] = get_order_id(entry, series)
        entry["*Customer Mobile"] = make_valid_ph_(entry["*Customer Mobile"])
        entry["Order Date as dd-mm-yyyy hh:MM"] = get_today()
        entry["*Master SKU"] = entry["*Product Name"]
        entry["*Partial COD (Yes/No)"] = "No"
        entry["Customer Alternate Mobile"] = make_valid_alternate_ph_num(
            entry["*Customer Mobile"],
            entry["Customer Alternate Mobile"]
        )
        entry["*Shipping Address Line 1"] = make_valid_addr(entry["*Shipping Address Line 1"])
        series[entry["*Product Name"].lower()] += 1
        
        merged_json_valid_entries.append(entry)
    except:
        print(it, entry["*Product Name"].strip().split(" "))
        print(f"\n\n\nINVALID\n\n{entry}\n\n\n")
        invalid_entries.append(entry)
        


# validation

for entry in merged_json_valid_entries:
    if not correct_ph_num(entry["*Customer Mobile"]):
        invalid_entries.append(entry)
        merged_json_valid_entries.remove(entry)
        print(f"\n\n\nPrimary\n\n\n")
        continue
    if not correct_ph_num(entry["Customer Alternate Mobile"]):
        invalid_entries.append(entry)
        merged_json_valid_entries.remove(entry)
        print(f"\n\n\nAlternate\n\n\n")
        continue
    if not correct_pincode(entry["*Shipping Address Postcode"]):
        print(f"\n\n\nPostcode\n\n\n")
        invalid_entries.append(entry)
        merged_json_valid_entries.remove(entry)
        continue
    if len(entry["*Shipping Address Line 1"]) >= 180:
        invalid_entries.append(entry)
        merged_json_valid_entries.remove(entry)
        continue



# Save as valid CSV
df_valid = pd.json_normalize(merged_json_valid_entries)
df_valid = df_valid[order]
df_valid.to_csv(os.path.join(OUTPUT_DIR, f"Order Upload File Valid {len(merged_json_valid_entries)}.csv"), index=False)


# Save as invalid CSV
# with open(os.path.join(OUTPUT_DIR, f"Invalid {len(invalid_entries)}.json"), 'w', encoding='utf-8') as file:
#     file.write(str(invalid_entries))



if len(invalid_entries):
    df_invalid = pd.json_normalize(invalid_entries)
    df_invalid = df_invalid[order + ["FILENAME, INDEX"]]
    df_invalid.to_csv(os.path.join(OUTPUT_DIR, f"Invalid {len(invalid_entries)}.csv"), index=False)

