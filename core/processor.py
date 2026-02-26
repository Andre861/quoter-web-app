import openpyxl
import pandas as pd
from io import BytesIO

def apply_markup_to_excel(wb, markup_percentage):
    """
    Applies the markup to the provided openpyxl workbook.
    """
    multiplier = 1 + (markup_percentage / 100)
    
    # Example logic: This assumes we are modifying a specific sheet/cell
    # In a real scenario, the user would need to configure which column/rows to target.
    # For now, this is a placeholder structure to represent formula injection.
    
    # We will need more sophisticated logic to find the 'Total' column dynamically.
    
    # Save the modified workbook to a BytesIO object for download
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.read()

def apply_markup_to_data(tables, markup_percentage):
    """
    Applies markup to extracted PDF table data (DataFrames).
    """
    multiplier = 1 + (markup_percentage / 100)
    marked_up_tables = []
    
    for df in tables:
        # Example logic: Assume the last column is the price.
        # This will need dynamic configuration based on the PDF structure.
        df_copy = df.copy()
        try:
            # Attempt to convert the last column to numeric and apply markup
            last_col = df_copy.columns[-1]
            original_col = df_copy[last_col].copy()
            
            # Strip currency symbols, commas, spaces
            clean_str = original_col.astype(str).str.replace(r'[\$, ]', '', regex=True)
            # Safely convert to numeric, turning bad parse values into NaNs
            numeric_col = pd.to_numeric(clean_str, errors='coerce')
            
            # Apply markup to only the valid numeric rows (NaN stays NaN)
            marked_up = numeric_col * multiplier
            
            # Format as two decimal places currency string
            formatted_col = marked_up.apply(lambda x: f"${x:,.2f}" if not pd.isna(x) else None)
            
            # Stitch it back: if formatted_col is None (meaning it wasn't numeric), use the original value
            df_copy[last_col] = formatted_col.combine_first(original_col)
            
        except Exception as e:
            # If conversion fails completely (e.g., column doesn't exist), skip gracefully
            print(f"Markup application failed on col {last_col}: {e}")
            pass
            
        marked_up_tables.append(df_copy)
        
    return marked_up_tables
