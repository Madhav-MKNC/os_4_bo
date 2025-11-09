import os
import pandas as pd
from validation import order, book_name_codes


def process_excel_file(input_path):
    df = pd.read_excel(input_path)

    out = pd.DataFrame()

    out["*Channel"] = "Custom"
    out["*Payment Method(COD/Prepaid)"] = "Prepaid"
    out["*Product Quantity"] = 1
    out["*Length (cm)"] = 10
    out["*Breadth (cm)"] = 10
    out["*Height (cm)"] = 10
    out["*Weight Of Shipment(kg)"] = 0.24
    out["*Selling Price(Per Unit Item, Inclusive of Tax)"] = 20
    out["*Partial COD (Yes/No)"] = "No"

    defaults = [
        "Customer Last Name", "Billing Address Line 1", "Billing Address Line 2",
        "Billing Address Country", "Billing Address State", "Billing Address City",
        "Billing Address Postcode", "Tax %", "Discount(Per Unit Item)",
        "Shipping Charges(Per Order)", "COD Charges(Per Order)",
        "Gift Wrap Charges(Per Order)", "Total Discount (Per Order)",
        "Send Notification(True/False)", "Comment", "HSN Code", "Location Id",
        "Reseller Name", "Company Name", "latitude", "longitude", "Verified Order",
        "Is documents", "Order Type", "Order tag", "Shipping Address Line 2",
        "*Master SKU", "*Order Id", "Order Date as dd-mm-yyyy hh:MM"
    ]
    for col in defaults:
        out[col] = ""

    # Mapped columns
    out["*Customer First Name"] = df["NAME"]
    out["Email (Optional)"] = df["EMAIL"]
    out["*Customer Mobile"] = df["PHONE"]
    out["Customer Alternate Mobile"] = df["ALTERNATE PHONE"]
    out["*Shipping Address Line 1"] = df["ADDRESS UPDATED"]
    # out["*Shipping Address Country"] = "df["COUNTRY CODE"]"
    out["*Shipping Address Country"] = "INDIA"
    out["*Shipping Address State"] = df["STATE"].fillna(df["STATE"])
    out["*Shipping Address City"] = df["DISTRICT"].fillna(df["DISTRICT"])
    out["*Shipping Address Postcode"] = df["PIN"]

    # Use lowercase mapping
    df["MAPPED_BOOK_NAME"] = (
        df["BOOK NAME"]
        .astype(str)
        .str.lower()
        .map(book_name_codes)
        .fillna(df["BOOK NAME"])
    )

    # Combine mapped name and language
    out["*Product Name"] = df["MAPPED_BOOK_NAME"].astype(str) + " " + df["BOOK LANG"].astype(str)

    # Save output CSV
    output_path = os.path.join("outputs", "output.csv")
    out.to_csv(output_path, index=False)

    print("✅ New CSV file created:", output_path)
    return output_path
