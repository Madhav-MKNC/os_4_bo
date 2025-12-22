"""
[PROMPT START]

Extract all barcode strings from the document, maintaining the order and extracting them page by page.
Export the extracted barcodes into a JSON file with the following structure:

```json
{
  "1": ["barcode1", "barcode2", ...],
  "2": ["barcode1", "barcode2", ...],
  ...
}
```

In the JSON output, the numbers (1, 2, ...) represent the page numbers,
and each page will contain an array of barcode strings extracted from that page.
Please provide only the downloadable JSON file once the extraction is complete.

[PROMPT END]
"""

import json
import os
import pandas as pd

from labels import constants
SENDER_PHONE = constants.SENDER_PHONE
WEIGHT = constants.WEIGHT
PrPdAmount = constants.PrPdAmount
PrPdType = constants.PrPdType

def read_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        barcodes = json.load(file)
    return barcodes


def generate_post_office_file(filepath, data):
    """Generate a CSV file with barcode data included.
    
    rows: Order ID	Forward ID	Shiprocket Created At	Channel	Status	
    Channel SKU	Master SKU	Product Name	Product Category	Product Quantity	
    Channel Created At	Customer Name	Customer Email	Customer Mobile	Customer Alternate Phone	
    Address Line 1	Address Line 2	Address City	Address State	Address Pincode	Payment Method	
    Product Price	Order Total	Tax	Tax %	Discount Value	Product HSN	Weight (KG)	Dimensions (CM)	Charged Weight	
    Courier Company	AWB Code	SRX Premium LM AWB	Shipping Bill URL	AWB Assigned Date	Pickup Location ID	
    Pickup Address Name	Pickup Scheduled Date	Order Picked Up Date	Pickup First Attempt Date	Pickedup Timestamp	
    Order Shipped Date	EDD	Delayed Reason	Order Delivered Date	RTO Address	RTO Initiated Date	RTO Delivered Date	
    COD Remittance Date	COD Payble Amount	Remitted Amount	CRF ID	UTR No	Zone	COD Charges	Freight Total Amount	
    Customer_invoice_id	Shipping Charges	Pickup Exception Reason	NPR1 Date	NPR1 Reason	NPR2 Date	NPR2 Reason	Latest NPR Date	Latest NPR Reason	
    First Out For Delivery Date	First_Pickup_Scheduled_Date	Buyer's Lat/long	Order Type	Order Tags	Invoice Date	
    Pickup Code	Eway Bill Nos	Last Updated AT	Partial COD Collected	Partial COD Value	RTO Score Charges	RTO Score Tax	
    Delivery Boost Charges	Delivery Boost Tax	WhatsApp Tracking Charges	WhatsApp Tracking Tax	
    Brand Boost Charges	Brand Boost Tax	NDR 1 Attempt Date	NDR 1 Remark	NDR 2 Attempt Date	NDR 2 Remark	
    NDR 3 Attempt Date	NDR 3 Remark	Latest NDR Date	Latest NDR Reason	Bridge Call Recording	Hub Address	Rto Risk	
    RAD Datetimestamp	BAG ID	Pickup Pincode	Verifier User ID	Verifier Email	Verifier Name	Attempt Count	Pickup Generated Date	
    RTO WayBill	RTO Risk	RTO Reason	Order Risk	Address Risk	Address Score	
    Lost Date	Latest OFD Date	Master Courier	Is Reverse	Exchange Order Type	Cancellation Reason
    
    """
    export_data = []
    for sl, row in enumerate(data):
        export_data.append({
            "SL": sl+1,
            "BARCODE": row.get("BARCODE"),
            "City": row.get("Address City"),
            "Pincode": row.get("Address Pincode"),
            "Name": row.get("Customer Name"),
            "ADD1": row.get("Address Line 1"),
            "ADDRMOBILE": row.get("Customer Mobile"),
            "SENDERMOBILE": SENDER_PHONE,
            "Weight": WEIGHT,
            "PrPdAmount": PrPdAmount,
            "PrPdType": PrPdType
        })

    df = pd.DataFrame(export_data)
    df.to_csv(filepath, index=False, encoding='utf-8')

