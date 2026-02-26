import pdfplumber
import pandas as pd
import openpyxl
import os
import io
from io import BytesIO
from google import genai
from google.genai import types

def extract_excel_data(file_bytes):
    """
    Extracts data from an uploaded Excel file.
    Returns: The loaded openpyxl workbook object.
    """
    # Load the workbook from the bytes, keeping data_only=False to preserve formulas
    wb = openpyxl.load_workbook(filename=BytesIO(file_bytes), data_only=False)
    return wb

def extract_pdf_data(file_bytes):
    """
    Extracts tabular data from an uploaded PDF using Gemini.
    Returns: A list of pandas DataFrames representing tables.
    """
    # Ensure API Key is set
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is missing. Please add it to your .env file.")
        
    client = genai.Client()
    
    prompt = """
You are a highly accurate data extraction tool.
I am providing you with a PDF document that contains quotation/invoice data.
Your objective is to extract ALL of the main tabular items/products data (e.g. description, quantity, unit price, total).
CRITICAL: You must extract EVERY SINGLE ROW across ALL PAGES of the document. Do NOT summarize. Do NOT omit any items.
Output the extracted table strictly in valid CSV format.
Do NOT wrap the output in markdown blocks (e.g. ```csv). Send back ONLY the raw CSV text.
The first row must contain the column headers.
"""
    try:
        # We upload the bare bytes to Gemini File API (requires generating a file-like object first if not local, 
        # but the new API supports inline base64 or direct bytes passing via the models.generate_content API)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=file_bytes,
                    mime_type='application/pdf',
                )
            ]
        )
        
        csv_text = response.text.strip()
        
        # If the model stubbornly returned markdown blocks, strip them
        if csv_text.startswith("```csv"):
            csv_text = csv_text[6:]
        if csv_text.startswith("```"):
            csv_text = csv_text[3:]
        if csv_text.endswith("```"):
            csv_text = csv_text[:-3]
            
        csv_text = csv_text.strip()
            
        if not csv_text:
            return []
            
        # Parse the CSV into a pandas DataFrame, skipping bad lines to prevent tokenizing errors
        df = pd.read_csv(io.StringIO(csv_text), on_bad_lines='skip')
        return [df]
        
    except Exception as e:
        print(f"Gemini extraction failed: {e}")
        raise ValueError(f"Gemini extraction failed: {e}")
