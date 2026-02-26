import streamlit as st
import pandas as pd
from dotenv import load_dotenv

import os
from supabase import create_client, Client

load_dotenv()

# --- Initialize Supabase ---
@st.cache_resource
def init_supabase() -> Client:
    url: str = os.environ.get("SUPABASE_URL", "")
    key: str = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)

supabase = init_supabase()

# --- Initialize Session State ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
st.set_page_config(page_title="Quoter", page_icon="📝", layout="wide")

import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- Login / Register UI ---
if not st.session_state.authenticated:
    try:
        bg_image = get_base64_of_bin_file("static/images/login_bg.png")
        bg_css = f"""
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.8)), url("data:image/png;base64,{bg_image}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #0f172a;
        }}
        """
    except Exception:
        bg_css = """
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
        }
        """

    st.markdown(f"""
        <style>
        {bg_css}
        
        /* Enlarged Typography for Title */
        .login-title {{
            text-align: center;
            font-size: 6.5rem;
            font-weight: 900;
            margin-bottom: -0.5rem;
            color: #0f172a;
            letter-spacing: -3px;
            text-shadow: 0 4px 15px rgba(255,255,255, 0.8);
        }}
        
        /* Highlight Accent on Title */
        .title-accent {{
            color: #3b82f6;
        }}
        
        .login-subtitle {{
            text-align: center;
            font-size: 1.4rem;
            color: #475569;
            margin-bottom: 3.5rem;
            font-weight: 500;
        }}
        
        /* Clean Solid White Container styling with wide feel */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(8px);
            border-radius: 16px !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 20px 40px -5px rgba(0, 0, 0, 0.1), 0 10px 15px -5px rgba(0, 0, 0, 0.04) !important;
            padding: 3rem 4rem !important;
        }}
        
        /* Vertical Centering */
        .block-container {{
            padding-top: 5rem;
            max-width: 1000px !important;
        }}
        
        /* High Contrast Input fields */
        div[data-baseweb="input"] {{
            background-color: #f1f5f9;
            border-radius: 8px;
            border: 2px solid transparent;
            transition: all 0.2s ease;
        }}
        
        div[data-baseweb="input"]:focus-within {{
            border-color: #3b82f6;
            background-color: #ffffff;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
        }}
        
        button[kind="primary"] {{
            background-color: #3b82f6;
            border: none;
            color: white;
            font-weight: 600;
            font-size: 1.2rem;
            border-radius: 8px;
            transition: all 0.2s ease;
            padding: 0.8rem 1rem;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2);
            margin-top: 1rem;
        }}
        
        button[kind="primary"]:hover {{
            background-color: #2563eb;
            transform: translateY(-2px);
            box-shadow: 0 8px 15px -3px rgba(59, 130, 246, 0.3);
        }}
        
        /* Form text colors */
        .stTextInput p, .stRadio p, label {{
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 1rem;
        }}
        
        /* Fix the error box if it appears */
        .stAlert {{
            background-color: #fef2f2;
            color: #991b1b;
            border: 1px solid #f87171;
            border-radius: 8px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Use columns to narrow the form width and center it
    _, col_center, _ = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown('<p class="login-title">Quot<span class="title-accent">er</span></p>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Simplify your pricing workflow.</p>', unsafe_allow_html=True)
        
        with st.container(border=True):
            auth_mode = st.radio("Select Action", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
            
            if not supabase:
                st.error("Supabase credentials are not configured properly. Please check your .env file.")
                st.stop()
                
            with st.form("auth_form", clear_on_submit=False):
                email = st.text_input("Work Email", placeholder="you@company.com")
                password = st.text_input("Password", type="password")
                
                submit_label = "Sign In" if auth_mode == "Login" else "Create Account"
                submit_btn = st.form_submit_button(submit_label, type="primary", use_container_width=True)
                
                if submit_btn:
                    if not email or not password:
                        st.error("Please provide both email and password.")
                    elif auth_mode == "Login":
                        try:
                            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                            st.session_state.authenticated = True
                            st.session_state.user_email = res.user.email
                            st.rerun()
                        except Exception as e:
                            st.error(f"Login failed: {e}")
                    elif auth_mode == "Register":
                        try:
                            res = supabase.auth.sign_up({"email": email, "password": password})
                            st.success("Registration successful! You can now log in.")
                        except Exception as e:
                            st.error(f"Registration failed: {e}")
                        
    st.stop() # Stop rendering the rest of the app if not authenticated

# --- Authenticated View ---
st.sidebar.markdown(f"**Logged in as:**<br>{st.session_state.user_email}", unsafe_allow_html=True)
if st.sidebar.button("Logout"):
    supabase.auth.sign_out()
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.rerun()

st.title("Quoter: Markup Generator")
st.write("Upload a retailer quotation to apply markup and generate client-ready files.")

# --- Mode Selection ---
st.header("Input Method")
input_mode = st.radio("How would you like to provide the quotation data?", ["Upload Existing Quote", "Manual Data Entry"], horizontal=True)

uploaded_file = None
proceed = False
file_type = None

if input_mode == "Upload Existing Quote":
    # --- File Upload Section ---
    uploaded_file = st.file_uploader(
        "Upload Retailer Quotation", 
        type=["pdf", "xlsx"],
        help="Accepts .pdf or .xlsx files only."
    )
    if uploaded_file is not None:
        proceed = True
        file_type = uploaded_file.name.split('.')[-1].lower()
        st.info(f"File uploaded successfully: {uploaded_file.name}")
    else:
        st.info("Please upload a file to begin.")
else:
    proceed = True
    file_type = "manual"

if proceed:
    # --- Input Fields Section ---
    st.header("Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Markup")
        markup_percentage = st.number_input(
            "Markup Percentage (%)", 
            min_value=0.0, 
            value=10.0, 
            step=1.0, 
            help="Enter the markup percentage to apply (e.g., 20 for 20%)."
        )
        
        st.subheader("Discounts & Taxes")
        discount_flat = st.number_input(
            "Discount (Flat $ Amount)", 
            min_value=0.0, 
            value=0.0, 
            step=10.0, 
            help="Enter a flat dollar amount to discount before tax."
        )
        tax_type = st.radio("Sales Tax Type", ["Percentage (%)", "Flat Amount ($)"], horizontal=True)
        if tax_type == "Percentage (%)":
            sales_tax_percentage = st.number_input(
                "Sales Tax (%)", 
                min_value=0.0, 
                value=0.0, 
                step=0.1, 
                help="Applied after markup and discount."
            )
            sales_tax_flat = 0.0
        else:
            sales_tax_flat = st.number_input(
                "Sales Tax ($)", 
                min_value=0.0, 
                value=0.0, 
                step=10.0, 
                help="Flat tax amount applied after markup and discount."
            )
            sales_tax_percentage = 0.0
        
        st.subheader("Sender Details")
        uploaded_logo = st.file_uploader("Company Logo (Optional)", type=["png", "jpg", "jpeg"])
        sender_name = st.text_input("Sender Company Name", value="My Company LLC")
        sender_email = st.text_input("Sender Email", value="sales@mycompany.com")
        sender_phone = st.text_input("Sender Phone", placeholder="+1 (555) 123-4567")
        sender_address = st.text_area("Sender Address", height=68, placeholder="123 Main St\nCity, State ZIP")
        
    with col2:
        st.subheader("Recipient Details")
        recipient_name = st.text_input("Client Company Name")
        recipient_contact = st.text_input("Client Contact Person")
        recipient_address = st.text_area("Client Address", height=68, placeholder="456 Client St\nCity, State ZIP")
        
    st.subheader("Job Details")
    job_description = st.text_area("Job Description / Notes", help="Add any context or description about this quotation.")
    signature_name = st.text_input("Signed By:", placeholder="John Doe", help="Name to appear in the signature block of the PDF.")
    
    st.markdown("---")
    
    # Reset session state if a new file is uploaded or mode switched
    if input_mode == "Upload Existing Quote":
        if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
            st.session_state.current_file = uploaded_file.name
            st.session_state.extracted_tables = None
            st.session_state.is_pdf = (file_type == 'pdf')
            st.session_state.is_manual = False
            st.session_state.generated_pdf = None
            st.session_state.generated_excel = None
    elif input_mode == "Manual Data Entry":
        if "is_manual" not in st.session_state or not st.session_state.is_manual:
            st.session_state.is_manual = True
            st.session_state.is_pdf = False
            # Initialize an empty DataFrame for manual entry with standard columns
            st.session_state.extracted_tables = [pd.DataFrame([{"Description": "", "Quantity": 1, "Unit Price": 0.0, "Total": 0.0}])]
            st.session_state.generated_pdf = None
            st.session_state.generated_excel = None
        
    # --- Step 1: Extract Data ---
    if st.session_state.is_pdf and st.session_state.extracted_tables is None:
        if st.button("Step 1: Extract Data from PDF"):
            with st.spinner("Analyzing PDF semantics..."):
                from core.extractor import extract_pdf_data
                try:
                    tables = extract_pdf_data(uploaded_file.getvalue())
                    if not tables:
                        st.warning("No tabular data could be found in this PDF.")
                    else:
                        st.session_state.extracted_tables = tables
                        # Reset generated files when extracting new data
                        st.session_state.generated_pdf = None
                        st.session_state.generated_excel = None
                        st.rerun()
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

    # --- Step 2: Edit and Generate ---
    if file_type == "xlsx" and not st.session_state.get("is_manual", False):
        # Excel workflow (Direct Process)
        if st.button("Generate Marked-up Excel", type="primary"):
            from core.extractor import extract_excel_data
            from core.processor import apply_markup_to_excel
            try:
                wb = extract_excel_data(uploaded_file.getvalue())
                marked_up_bytes = apply_markup_to_excel(wb, markup_percentage)
                st.success("Excel processed successfully!")
                file_name_out = f"MarkedUp_{uploaded_file.name}" if uploaded_file else "Quotation_MarkedUp.xlsx"
                st.download_button("Download Marked-up Excel", data=marked_up_bytes, file_name=file_name_out)
            except Exception as e:
                st.error(f"Processing failed: {e}")
                
    elif st.session_state.extracted_tables is not None:
        # Only show the editable grid if we are in Manual Mode OR we successfully extracted PDF data
        show_editor = False
        if input_mode == "Manual Data Entry":
            show_editor = True
            st.subheader("Step 1: Enter Quotation Data")
            st.write("Enter your items below. The 'Total' column will be automatically calculated as (Quantity × Unit Price) when you generate!")
        elif input_mode == "Upload Existing Quote" and file_type == "pdf":
            show_editor = True
            col_head1, col_head2 = st.columns([4, 1])
            with col_head1:
                st.subheader("Step 2: Review and Correct Extracted Data")
            with col_head2:
                if st.button("🔄 Retry Extraction", help="If the data looks wrong, click here to extract it again.", use_container_width=True):
                    st.session_state.extracted_tables = None
                    st.rerun()
            st.write("You can edit the cells below directly. Ensure numeric columns are clean (e.g., '100.50' instead of '$100.50').")
            
        edited_tables = []
        if show_editor:
            for idx, df in enumerate(st.session_state.extracted_tables):
                # Show the interactive data editor
                edited_df = st.data_editor(df, num_rows="dynamic", key=f"editor_{idx}", use_container_width=True)
                edited_tables.append(edited_df)
                
            st.markdown("---")
            btn_label = "Step 2: Generate Final Quotations" if st.session_state.get("is_manual", False) else "Step 3: Generate Final Quotations"
            if st.button(btn_label, type="primary"):
                with st.spinner("Applying markup and generating files..."):
                    from core.processor import apply_markup_to_data
                    from core.generator import generate_final_pdf, generate_excel_from_pdf
                    import pandas as pd
                    
                    logo_base64 = None
                    logo_mime = "image/png"
                    if uploaded_logo:
                        # Extract base64 dynamically from uploaded file
                        import base64
                        logo_base64 = base64.b64encode(uploaded_logo.getvalue()).decode()
                        logo_mime = uploaded_logo.type

                    config = {
                        "logo_base64": logo_base64,
                        "logo_mime": logo_mime,
                        "sender_name": sender_name,
                        "sender_email": sender_email,
                        "sender_phone": sender_phone,
                        "sender_address": sender_address,
                        "recipient_name": recipient_name,
                        "recipient_contact": recipient_contact,
                        "recipient_address": recipient_address,
                        "job_description": job_description,
                        "discount_flat": discount_flat,
                        "tax_type": "percentage" if tax_type == "Percentage (%)" else "flat",
                        "sales_tax_percentage": sales_tax_percentage,
                        "sales_tax_flat": sales_tax_flat,
                        "signature_name": signature_name
                    }
                    
                    try:
                        # Calculate Total = Quantity * Unit Price dynamically for any row
                        for df in edited_tables:
                            if "Quantity" in df.columns and "Unit Price" in df.columns and "Total" in df.columns:
                                q = pd.to_numeric(df["Quantity"], errors='coerce').fillna(1)
                                p = pd.to_numeric(df["Unit Price"], errors='coerce').fillna(0)
                                calc_total = q * p
                                
                                # Only overwrite Total if we calculated something != 0.
                                # This allows users to type direct values into 'Total' for things like 'Shipping'
                                user_total = pd.to_numeric(df["Total"], errors='coerce').fillna(0)
                                df["Total"] = calc_total.where(calc_total != 0, user_total)
                                    
                        # Apply markup correctly
                        marked_up_tables = apply_markup_to_data(edited_tables, markup_percentage)
                        
                        # Smartly rename and filter columns to the core 4 to ensure totals calculation succeeds
                        clean_tables = []
                        for mt in marked_up_tables:
                            rename_map = {}
                            cols_to_keep = []
                            for c in mt.columns:
                                cl = str(c).lower()
                                if 'total' in cl or 'amount' in cl: rename_map[c] = 'Total'
                                elif 'price' in cl or 'unit' in cl or 'cost' in cl: rename_map[c] = 'Unit Price'
                                elif 'qty' in cl or 'quant' in cl: rename_map[c] = 'Quantity'
                                elif 'desc' in cl or 'item' in cl: rename_map[c] = 'Description'
                                
                                if c in rename_map: cols_to_keep.append(c)
                                
                            # If no standard columns were found, keep everything to be safe
                            if not cols_to_keep:
                                cols_to_keep = list(mt.columns)
                                
                            clean_mt = mt[cols_to_keep].copy()
                            clean_mt.rename(columns=rename_map, inplace=True)
                            
                            # Drop duplicated column names if they mapped to the same target
                            if len(clean_mt.columns) != len(set(clean_mt.columns)):
                                clean_mt = clean_mt.loc[:, ~clean_mt.columns.duplicated()]
                                
                            # Reorder to exactly [Description, Quantity, Unit Price, Total]
                            final_order = [c for c in ["Description", "Quantity", "Unit Price", "Total"] if c in clean_mt.columns]
                            if final_order:
                                clean_mt = clean_mt[final_order + [c for c in clean_mt.columns if c not in final_order]]
                                
                            # Fill NaNs with empty string so "NaN" doesn't print on the PDF
                            clean_mt = clean_mt.fillna("")
                            clean_tables.append(clean_mt)
                            
                        # Calculate Subtotal over all CLEANED tables using the guaranteed "Total" column
                        subtotal = 0.0
                        for mt in clean_tables:
                            if not mt.empty and "Total" in mt.columns:
                                try:
                                    # Safely stringify to remove currency symbols before summing
                                    clean_col = mt["Total"].astype(str).str.replace(r'[\$,]', '', regex=True)
                                    total_val = pd.to_numeric(clean_col, errors='coerce').fillna(0).sum()
                                    subtotal += total_val
                                except Exception as sum_e:
                                    print(f"Summing error on Total column:", sum_e)
                            
                        running_total = subtotal
                        discount_val = discount_flat
                        running_total -= discount_val
                        if running_total < 0: running_total = 0.0
                        
                        tax_amount = 0.0
                        if tax_type == "Percentage (%)" and sales_tax_percentage > 0:
                            tax_amount = running_total * (sales_tax_percentage / 100.0)
                        elif tax_type == "Flat Amount ($)" and sales_tax_flat > 0:
                            tax_amount = sales_tax_flat
                            
                        running_total += tax_amount
                        grand_total = running_total
                        
                        markup_amount = 0.0
                        if markup_percentage > 0:
                            multiplier = 1 + (markup_percentage / 100.0)
                            base_subtotal = subtotal / multiplier
                            markup_amount = subtotal - base_subtotal
                        
                        config["calc_subtotal"] = subtotal
                        config["calc_discount"] = discount_val
                        config["calc_tax"] = tax_amount
                        config["calc_markup"] = markup_amount
                        config["calc_grand_total"] = grand_total
                        config["sales_tax_percentage"] = sales_tax_percentage
                        config["tax_type"] = tax_type
                        config["markup_percentage"] = markup_percentage

                        # Use the specifically filtered tables instead of raw edited
                        pdf_bytes = generate_final_pdf(clean_tables, config)
                        excel_from_pdf_bytes = generate_excel_from_pdf(edited_tables, config, markup_percentage)
                        
                        # Store generated files in session state so downloading one doesn't erase the other
                        st.session_state.generated_pdf = pdf_bytes
                        st.session_state.generated_excel = excel_from_pdf_bytes
                        st.success("Files generated successfully!")
                        
                    except Exception as e:
                        st.error(f"File generation failed: {e}")
                        
            # Always show download buttons if files exist in session state
            # (Indent fixed so this block only shows if show_editor is True, or if button was clicked)
            if st.session_state.get("generated_pdf") or st.session_state.get("generated_excel"):
                colA, colB = st.columns(2)
                with colA:
                    if st.session_state.get("generated_pdf"):
                        st.download_button("Download Resulting PDF", data=st.session_state.generated_pdf, file_name="Quotation_MarkedUp.pdf", mime="application/pdf")
                with colB:
                    if st.session_state.get("generated_excel"):
                        st.download_button("Download Resulting Excel (with Formulas)", data=st.session_state.generated_excel, file_name="Quotation_MarkedUp.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                        
                # --- Step 3: PDF Preview ---
                if st.session_state.get("generated_pdf"):
                    st.markdown("---")
                    st.subheader("Step 3: Preview Final PDF")
                    import base64
                    base64_pdf = base64.b64encode(st.session_state.generated_pdf).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="600" height="600" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
        
