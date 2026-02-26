# Quoter: Markup Generator

Quoter is a Streamlit-based web application designed to help businesses process retailer quotations, apply custom markup percentages, handles sales tax and discounts, and generate beautiful, client-ready PDF and Excel files. 

It features two primary workflows:
1. **Upload Existing Quote:** Upload a PDF (parsed seamlessly via Google Gemini AI) or an Excel (`.xlsx`) quotation. 
2. **Manual Data Entry:** Build your quotation from scratch using a fast, interactive data grid.

## Prerequisites

To run this application on any system, you need three core components installed:

1. **Python 3.9+**
2. **wkhtmltopdf**: A command line tool to render HTML into PDF using the Qt WebKit rendering engine. (Required for the `pdfkit` library).
3. **Google Gemini API Key**: Used for extracting tabular data from unstructured PDF uploads.

## System Installations

### Step 1: Install wkhtmltopdf
This is a required system-level dependency.
* **Windows:** Download the installer from the [official wkhtmltopdf releases](https://wkhtmltopdf.org/downloads.html) and run it. Ensure you add the installed `/bin` directory to your system's `PATH`.
* **macOS (via Homebrew):** `brew install homebrew/cask/wkhtmltopdf`
* **Linux (Ubuntu/Debian):** `sudo apt-get install wkhtmltopdf`

### Step 2: Clone & Set Up the Python Environment
Open your terminal or command prompt and run the following commands:

```bash
# 1. Clone or download this project directory
cd Quoter

# 2. Create a virtual environment (recommended)
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS and Linux:
source venv/bin/activate

# 4. Install the required Python packages
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
The application requires your API keys to be securely stored in a `.env` file within the root directory of the project.

1. Create a file named `.env` in the `Quoter` folder.
2. Add your Gemini API key inside the `.env` file in the following format:
```ini
GEMINI_API_KEY=your_actual_api_key_here
```

## Running the Application

Once your virtual environment is activated and dependencies are installed, you can launch the application:

```bash
streamlit run app.py
```

This will automatically open your default web browser to `http://localhost:8501`.

## Usage Guide
1. **Select Input Method:** Choose between "Upload Existing Quote" or "Manual Data Entry".
2. **Configure Settings:** Set your Markup Percentage, Sender/Recipient Details, Job Description, Discount (Flat $ Amount), and Sales Tax (toggle between Percentage or Flat Amount).
3. **Review/Edit Data:** 
   * If you uploaded a PDF, click "Step 1: Extract Data". 
   * A beautiful, interactive data grid will appear. You can fix any OCR errors or add/remove rows here directly!
   * **Smart Auto-Calculation:** If you add new rows manually or use "Manual Data Entry" mode, the app will automatically calculate the `Total` (Quantity × Unit Price) for you. (Note: Typing a strict flat fee into the Total column overrides this for items like "Shipping").
4. **Generate & Preview:** Click "Generate Final Quotations". The tool applies your markup, calculates all math flawlessly, and instantly presents a **live 600x600 PDF preview** right in your browser. All generated files include dynamic "Generated: [Date]" timestamps.
5. **Download:** Click the buttons to download your professional PDF and live-formula Excel documents.
