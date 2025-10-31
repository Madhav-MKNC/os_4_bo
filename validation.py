from datetime import datetime
import re
import pandas as pd

# 
def get_today():
    return datetime.now().strftime("%d-%m-%Y %H:%M")

# 
def get_day():
    today = get_today()
    today_obj = datetime.strptime(today, "%d-%m-%Y %H:%M")
    return today_obj.strftime("%d%b%y").upper()

# 
lang_codes = {
    'english': 'EN', 'hindi': 'HI',
    'kannada': 'KA', 'kannad': 'KA',
    'telugu': 'TL', 'tamil': 'TA', 'malayalam': 'MA',
    'marathi': 'MH', 'gujarati': 'GJ', 'punjabi': 'PB',
    'bengali': 'BG', 'nepali': 'NE',
    'odia': 'OD', 'odiya': 'OD', 'oriya': 'OD',
    'assamese': 'AS', 'manipuri': 'MN', 'bodo': 'BO',
    'urdu': 'UR', 'sindhi': 'SN'
}

# 
def correct_ph_num(ph_num_str):
    if isinstance(ph_num_str, str):
        if ph_num_str.lower() == "nan": return False
    try:
        ph_num_str = float(ph_num_str)
    except:
        pass
    if not ph_num_str: return True
    ph_num_str = str(int(ph_num_str))
    return len(ph_num_str) == 10


def make_valid_addr(addr_str):
    addr_str = re.sub(r'Pin\s*\d{6}\s*Ph.*', '', addr_str, flags=re.IGNORECASE)
    if "#" in addr_str:
        addr_str = addr_str[addr_str.index("#"):]
    return addr_str.strip()


def correct_pincode(pin):
    return len(str(pin).replace('.0', '')) == 6



def make_valid_ph_(num):
    if not pd.notna(num):
        return ""
    num = str(int(num))
    return num
    
    
    
def make_valid_alternate_ph_num(primary_num, alternate_num):
    if not pd.notna(alternate_num):
        return ""
    nums = str(alternate_num).strip().split(",")
    for i in nums:
        x = str(int(i.replace('.0', '')))
        if x != str(int(primary_num)):
            return i
    return nums[0]

#
def get_order_id(entry, series: dict):
    # KAGGTM30OCT2500470
    order_id = "KA"

    # print(entry["*Product Name"].strip().split(" "))
    temp_xy = entry["*Product Name"].strip().split(" ")
    # print(temp_xy)
    bookname = " ".join(temp_xy[:-1])
    lang = temp_xy[-1]
    
    # bookname = [0]
    # lang = entry["*Product Name"].split(" ")[1]

    order_id += bookname + lang_codes[lang.lower()]

    day = get_day()
    order_id += day

    if entry["*Product Name"].lower() not in series:
        series[entry["*Product Name"].lower()] = 0
    sno = series[entry["*Product Name"].lower()] + 1
    series_id = f"{sno:05}"
    order_id += series_id

    return order_id

order = [
    "*Order Id",
    "Order Date as dd-mm-yyyy hh:MM",
    "*Channel",
    "*Payment Method(COD/Prepaid)",
    "*Customer First Name",
    "Customer Last Name",
    "Email (Optional)",
    "*Customer Mobile",
    "Customer Alternate Mobile",
    "*Shipping Address Line 1",
    "Shipping Address Line 2",
    "*Shipping Address Country",
    "*Shipping Address State",
    "*Shipping Address City",
    "*Shipping Address Postcode",
    "Billing Address Line 1",
    "Billing Address Line 2",
    "Billing Address Country",
    "Billing Address State",
    "Billing Address City",
    "Billing Address Postcode",
    "*Master SKU",
    "*Product Name",
    "*Product Quantity",
    "Tax %",
    "*Selling Price(Per Unit Item, Inclusive of Tax)",
    "Discount(Per Unit Item)",
    "Shipping Charges(Per Order)",
    "COD Charges(Per Order)",
    "Gift Wrap Charges(Per Order)",
    "Total Discount (Per Order)",
    "*Partial COD (Yes/No)",
    "*Length (cm)",
    "*Breadth (cm)",
    "*Height (cm)",
    "*Weight Of Shipment(kg)",
    "Send Notification(True/False)",
    "Comment",
    "HSN Code",
    "Location Id",
    "Reseller Name",
    "Company Name",
    "latitude",
    "longitude",
    "Verified Order",
    "Is documents",
    "Order Type",
    "Order tag",
]


