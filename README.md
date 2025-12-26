# PDF Data Extractor

A Streamlit application that intelligently extracts data from PDFs and converts them to Excel or CSV format.

## Features

- **Auto-detect PDF type**: Automatically identifies whether your PDF is text-based, scanned, or a mixed report
- **Multiple extraction methods**: 
  - Text-based PDFs with tables (using tabula-py/pdfplumber)
  - Scanned/Image-based PDFs (using OCR)
  - Mixed content reports (comprehensive extraction)
- **Flexible output**: Download as CSV or Excel
- **User control**: Override auto-detection if needed
- **Preview**: See extracted data before downloading

## Tech Stack

- **Streamlit**: Web interface
- **pdfplumber**: PDF text and table extraction
- **tabula-py**: Table extraction
- **pytesseract**: OCR for scanned documents
- **pdf2image**: Convert PDF pages to images for OCR
- **pandas**: Data manipulation
- **openpyxl**: Excel file generation

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd pdf-extractor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install system dependencies (for OCR)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr poppler-utils

# macOS:
brew install tesseract poppler
```

## Usage

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

## Project Structure

```
pdf-extractor/
├── app.py                 # Main Streamlit application
├── extractors/
│   ├── __init__.py
│   ├── text_table.py     # Text-based PDF extraction
│   ├── scanned.py        # OCR-based extraction
│   └── report.py         # Mixed content extraction
├── utils/
│   ├── __init__.py
│   ├── detector.py       # Auto-detect PDF type
│   └── converters.py     # Format conversion utilities
├── requirements.txt
└── README.md
```

## How It Works

1. Upload your PDF file
2. The app auto-detects the PDF type (or you can manually select)
3. Choose your preferred extraction method
4. Preview the extracted data
5. Download as CSV or Excel

## Future Enhancements

- Batch processing multiple PDFs
- Custom column mapping
- Data validation and cleaning
- Support for more output formats
- Cloud storage integration

## Contributing

Feel free to open issues or submit pull requests!

## License

MIT License
