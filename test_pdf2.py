import pandas as pd
from core.generator import generate_final_pdf

# Mock messy data that Gemini might output
df = pd.DataFrame([{
    "Description ": "Roofing Labor",
    "Qty": "1",
    "Unit Price": "$500.00",
    "Total Price": "$500.00"
}])

# Same cleaning logic from app.py
clean_tables = []
for mt in [df]:
    rename_map = {}
    cols_to_keep = []
    for c in mt.columns:
        cl = str(c).lower()
        if 'total' in cl or 'amount' in cl: rename_map[c] = 'Total'
        elif 'price' in cl or 'unit' in cl or 'cost' in cl: rename_map[c] = 'Unit Price'
        elif 'qty' in cl or 'quant' in cl: rename_map[c] = 'Quantity'
        elif 'desc' in cl or 'item' in cl: rename_map[c] = 'Description'
        
        if c in rename_map: cols_to_keep.append(c)
        
    if not cols_to_keep:
        cols_to_keep = list(mt.columns)
        
    clean_mt = mt[cols_to_keep].copy()
    clean_mt.rename(columns=rename_map, inplace=True)
    
    if len(clean_mt.columns) != len(set(clean_mt.columns)):
        clean_mt = clean_mt.loc[:, ~clean_mt.columns.duplicated()]
        
    final_order = [c for c in ["Description", "Quantity", "Unit Price", "Total"] if c in clean_mt.columns]
    if final_order:
        clean_mt = clean_mt[final_order + [c for c in clean_mt.columns if c not in final_order]]
        
    clean_mt = clean_mt.fillna("")
    clean_tables.append(clean_mt)

print("Cleaned DataFrame:")
print(clean_tables[0])

# Subtotal
subtotal = 0.0
for mt in clean_tables:
    if not mt.empty and "Total" in mt.columns:
        clean_col = mt["Total"].astype(str).str.replace(r'[\$,]', '', regex=True)
        total_val = pd.to_numeric(clean_col, errors='coerce').fillna(0).sum()
        subtotal += total_val
print("Calculated Subtotal:", subtotal)
