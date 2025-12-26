"""
Scanned/Image-based PDF Extractor
Uses OCR (pytesseract) to extract text from scanned PDFs
"""

import pandas as pd
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
from typing import List, Tuple
import re


def extract_text_from_scanned_pdf(pdf_file, dpi: int = 300) -> Tuple[str, dict]:
    """
    Extract text from scanned PDF using OCR
    
    Args:
        pdf_file: Uploaded PDF file object
        dpi: DPI for image conversion (higher = better quality but slower)
        
    Returns:
        Tuple of (extracted text, metadata dict)
    """
    
    metadata = {
        'method': 'OCR (tesseract)',
        'pages_processed': 0,
        'total_text_length': 0,
        'errors': [],
        'dpi': dpi
    }
    
    all_text = []
    
    try:
        pdf_file.seek(0)
        
        # Convert PDF to images
        images = convert_from_bytes(pdf_file.read(), dpi=dpi)
        metadata['pages_processed'] = len(images)
        
        # OCR each page
        for page_num, image in enumerate(images, 1):
            try:
                # Perform OCR
                text = pytesseract.image_to_string(image, lang='eng')
                
                if text.strip():
                    all_text.append(f"--- Page {page_num} ---\n{text}\n")
                
            except Exception as e:
                metadata['errors'].append(f"Page {page_num}: {str(e)}")
        
        # Combine all text
        full_text = "\n".join(all_text)
        metadata['total_text_length'] = len(full_text)
        
        pdf_file.seek(0)
        
        return full_text, metadata
        
    except Exception as e:
        metadata['errors'].append(f"General OCR error: {str(e)}")
        pdf_file.seek(0)
        return "", metadata


def text_to_dataframe(text: str) -> pd.DataFrame:
    """
    Convert extracted text to a simple DataFrame
    Attempts to detect structure in the text
    
    Args:
        text: Extracted text string
        
    Returns:
        DataFrame with text content
    """
    
    # Split by lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        return pd.DataFrame({'Text': ['No text extracted']})
    
    # Try to detect if text has tabular structure (multiple columns separated by spaces/tabs)
    # Check if lines have consistent number of "words"
    word_counts = [len(line.split()) for line in lines[:10]]  # Sample first 10 lines
    
    if word_counts and max(word_counts) > 1 and len(set(word_counts)) <= 3:
        # Looks like tabular data
        # Try to split by multiple spaces or tabs
        rows = []
        for line in lines:
            # Split by 2+ spaces or tabs
            parts = re.split(r'\s{2,}|\t+', line)
            rows.append(parts)
        
        # Find max columns
        max_cols = max(len(row) for row in rows)
        
        # Pad rows to same length
        padded_rows = [row + [''] * (max_cols - len(row)) for row in rows]
        
        # First row as header if it looks like text (not numbers)
        if padded_rows and not any(part.replace('.', '').replace(',', '').isdigit() 
                                   for part in padded_rows[0]):
            df = pd.DataFrame(padded_rows[1:], columns=padded_rows[0])
        else:
            df = pd.DataFrame(padded_rows)
            
    else:
        # Not tabular, just return as single column
        df = pd.DataFrame({'Extracted_Text': lines})
    
    return df


def extract_scanned_pdf(pdf_file, output_format: str = 'text') -> Tuple[pd.DataFrame, dict]:
    """
    Main extraction function for scanned PDFs
    
    Args:
        pdf_file: Uploaded PDF file object
        output_format: 'text' (simple text column) or 'auto' (try to detect structure)
        
    Returns:
        Tuple of (DataFrame, metadata dict)
    """
    
    # Extract text using OCR
    text, metadata = extract_text_from_scanned_pdf(pdf_file)
    
    # Convert to DataFrame
    if output_format == 'auto':
        df = text_to_dataframe(text)
    else:
        # Simple text output
        lines = [line for line in text.split('\n') if line.strip()]
        df = pd.DataFrame({'Extracted_Text': lines if lines else ['No text extracted']})
    
    metadata['output_format'] = output_format
    
    return df, metadata


def ocr_with_table_detection(pdf_file, dpi: int = 300) -> Tuple[List[pd.DataFrame], dict]:
    """
    Advanced OCR with table detection
    Attempts to identify and extract tables from scanned PDFs
    
    Args:
        pdf_file: Uploaded PDF file object
        dpi: DPI for image conversion
        
    Returns:
        Tuple of (list of DataFrames, metadata dict)
    """
    
    # Note: This is a simplified version
    # For production, you might want to use libraries like:
    # - img2table
    # - camelot-py with image mode
    # - AWS Textract or Google Vision API
    
    metadata = {
        'method': 'OCR with table detection',
        'note': 'Using basic text extraction - consider advanced tools for complex tables',
        'errors': []
    }
    
    # For now, use the standard OCR
    df, ocr_metadata = extract_scanned_pdf(pdf_file, output_format='auto')
    metadata.update(ocr_metadata)
    
    return [df], metadata
