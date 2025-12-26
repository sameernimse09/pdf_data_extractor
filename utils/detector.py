"""
PDF Type Detector
Automatically detects the type of PDF (text-based, scanned, or mixed report)
"""

import pdfplumber
import PyPDF2
from typing import Tuple


def detect_pdf_type(pdf_file) -> Tuple[str, dict]:
    """
    Detect the type of PDF and return classification with confidence metrics
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        Tuple of (pdf_type, metadata)
        pdf_type: One of 'text_tables', 'scanned', 'report'
        metadata: Dict with detection details
    """
    
    metadata = {
        'total_pages': 0,
        'has_text': False,
        'has_tables': False,
        'text_percentage': 0,
        'confidence': 'high'
    }
    
    try:
        # Reset file pointer
        pdf_file.seek(0)
        
        # Check with pdfplumber for text and tables
        with pdfplumber.open(pdf_file) as pdf:
            metadata['total_pages'] = len(pdf.pages)
            
            total_chars = 0
            pages_with_text = 0
            pages_with_tables = 0
            
            # Sample first 3 pages for performance
            sample_pages = min(3, len(pdf.pages))
            
            for i in range(sample_pages):
                page = pdf.pages[i]
                
                # Check for extractable text
                text = page.extract_text()
                if text and len(text.strip()) > 50:  # Minimum text threshold
                    pages_with_text += 1
                    total_chars += len(text.strip())
                
                # Check for tables
                tables = page.extract_tables()
                if tables and len(tables) > 0:
                    pages_with_tables += 1
            
            # Calculate metrics
            metadata['has_text'] = pages_with_text > 0
            metadata['has_tables'] = pages_with_tables > 0
            metadata['text_percentage'] = (pages_with_text / sample_pages) * 100
            
            # Classify PDF type
            if not metadata['has_text'] or metadata['text_percentage'] < 20:
                # Very little or no extractable text = scanned
                pdf_type = 'scanned'
                metadata['confidence'] = 'high'
                
            elif metadata['has_tables'] and metadata['text_percentage'] > 70:
                # Has tables and good text extraction = text-based with tables
                pdf_type = 'text_tables'
                metadata['confidence'] = 'high'
                
            elif metadata['has_text'] and not metadata['has_tables']:
                # Text but no clear tables = report/document
                pdf_type = 'report'
                metadata['confidence'] = 'medium'
                
            else:
                # Mixed scenario - default to report
                pdf_type = 'report'
                metadata['confidence'] = 'medium'
        
        # Reset file pointer for next use
        pdf_file.seek(0)
        
        return pdf_type, metadata
        
    except Exception as e:
        # If detection fails, default to safest option
        print(f"Detection error: {str(e)}")
        metadata['confidence'] = 'low'
        pdf_file.seek(0)
        return 'text_tables', metadata


def get_pdf_type_description(pdf_type: str) -> str:
    """Return user-friendly description of PDF type"""
    
    descriptions = {
        'text_tables': '📊 Text-based PDF with Tables',
        'scanned': '📷 Scanned/Image-based PDF (requires OCR)',
        'report': '📄 Text Report/Document'
    }
    
    return descriptions.get(pdf_type, 'Unknown PDF type')


def get_extraction_method_info(pdf_type: str) -> str:
    """Return information about the extraction method that will be used"""
    
    info = {
        'text_tables': 'Will use pdfplumber/tabula for high-quality table extraction',
        'scanned': 'Will use OCR (Tesseract) to extract text from images',
        'report': 'Will extract all text and any embedded tables using pdfplumber'
    }
    
    return info.get(pdf_type, '')
