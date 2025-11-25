import pandas as pd
import chardet

def csv_to_json(file_path):
    """Convert a CSV file into JSON-like Python dictionaries with safe encoding detection."""
    
    # Detect encoding safely
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(100000))
    encoding = result.get('encoding', 'utf-8')
    
    # Try reading CSV with multiple fallbacks
    try:
        df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1', low_memory=False)
    except Exception as e:
        raise ValueError(f"Could not read CSV file: {e}")

    # Fill NaN values with empty strings to prevent errors
    df = df.fillna("")
    return df.to_dict(orient="records")

def get_data(filepath) -> list:
    """
    Extracts specific columns for the label generator.
    Note: 'to' is the destination, 'from' is the sender.
    """
    raw_data = csv_to_json(filepath)
    processed_data = []

    for entry in raw_data:
        to_address = entry.get("*Shipping Address Line 1")
        if not to_address:
            print(entry)
            raise ValueError("Missing required field: '*Shipping Address Line 1'")

        item_name = entry.get("*Product Name")
        if not item_name:
            print(entry)
            raise ValueError("Missing required field: '*Product Name'")

        processed_data.append({
            "to": to_address,
            "item": item_name
        })

    return processed_data
