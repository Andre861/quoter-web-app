import pandas as pd
from core.generator import generate_final_pdf

df = pd.DataFrame([{
    "Description": "Test Item",
    "Quantity": 2,
    "Unit Price": 100.0,
    "Total": 200.0
}])

config = {
    "calc_subtotal": 200.0,
    "calc_discount": 0.0,
    "calc_tax": 10.0,
    "calc_grand_total": 210.0,
    "sales_tax_percentage": 5.0,
    "tax_type": "percentage",
    "signature_name": "Test Signature",
    "logo_mime": "image/png",
    "logo_base64": ""
}

pdf_bytes = generate_final_pdf([df], config)
with open("test.pdf", "wb") as f:
    f.write(pdf_bytes)
print("PDF generated successfully.")
