# Quick Start Guide

## Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd pdf-extractor
```

2. **Create and activate virtual environment**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Install system dependencies**

**For Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils default-jre
```

**For macOS:**
```bash
brew install tesseract poppler openjdk
```

**For Windows:**
- Download and install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download and install Poppler: http://blog.alivate.com.au/poppler-windows/
- Add both to your PATH environment variable
- Install Java JRE for tabula-py

## Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Testing the Application

1. **Prepare test PDFs**
   - Text-based PDF with tables (e.g., a financial report)
   - Scanned PDF (e.g., a scanned invoice)
   - Mixed content report

2. **Upload and test**
   - Upload each PDF type
   - Verify auto-detection works
   - Try manual override
   - Test both CSV and Excel downloads

3. **Check extraction quality**
   - Verify tables are correctly extracted
   - Check OCR accuracy for scanned documents
   - Ensure text extraction is clean

## Common Issues

### Issue: "tesseract not found"
**Solution**: Make sure Tesseract is installed and added to PATH

### Issue: "Java not found" (for tabula)
**Solution**: Install Java JRE and ensure it's in PATH

### Issue: PDF extraction returns empty data
**Solution**: 
- Check if PDF is password-protected
- Verify PDF has extractable content
- Try different extraction methods

### Issue: Slow extraction for scanned PDFs
**Solution**: This is normal - OCR is computationally intensive. For large files, consider reducing DPI in the code.

## Customization

### Change OCR Language
Edit `extractors/scanned.py`:
```python
text = pytesseract.image_to_string(image, lang='spa')  # For Spanish
```

### Adjust OCR Quality
Edit `extractors/scanned.py`:
```python
images = convert_from_bytes(pdf_file.read(), dpi=150)  # Lower for speed, higher for quality
```

### Add More Export Formats
Edit `utils/converters.py` to add JSON, XML, or other formats.

## Next Steps

- Add more test cases
- Deploy to cloud (Streamlit Cloud, Heroku, etc.)
- Add batch processing
- Implement data validation
- Add user authentication for multi-user scenarios

## Support

For issues or questions, please open an issue on GitHub.
