"""
Text-based PDF with Tables Extractor
Uses pdfplumber and tabula-py for extracting tables from text-based PDFs
"""

import pdfplumber
import tabula
import pandas as pd
from typing import List, Tuple
import tempfile
import os


def extract_with_pdfplumber(pdf_file) -> Tuple[List[pd.DataFrame], dict]:
    """
    Extract tables using pdfplumber
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        Tuple of (list of DataFrames, metadata dict)
    """
    tables = []
    metadata = {
        'method': 'pdfplumber',
        'total_tables': 0,
        'pages_processed': 0,
        'errors': []
    }
    
    try:
        pdf_file.seek(0)
        
        with pdfplumber.open(pdf_file) as pdf:
            metadata['pages_processed'] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # Extract tables from page
                    page_tables = page.extract_tables()
                    
                    if page_tables:
                        for table_num, table in enumerate(page_tables, 1):
                            if table and len(table) > 0:
                                # Convert to DataFrame
                                # First row as header if it looks like headers
                                df = pd.DataFrame(table[1:], columns=table[0])
                                
                                # Add metadata
                                df.attrs['page'] = page_num
                                df.attrs['table_num'] = table_num
                                
                                tables.append(df)
                                
                except Exception as e:
                    metadata['errors'].append(f"Page {page_num}: {str(e)}")
            
            metadata['total_tables'] = len(tables)
        
        pdf_file.seek(0)
        
    except Exception as e:
        metadata['errors'].append(f"General error: {str(e)}")
    
    return tables, metadata


def extract_with_tabula(pdf_file) -> Tuple[List[pd.DataFrame], dict]:
    """
    Extract tables using tabula-py
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        Tuple of (list of DataFrames, metadata dict)
    """
    tables = []
    metadata = {
        'method': 'tabula',
        'total_tables': 0,
        'pages_processed': 0,
        'errors': []
    }
    
    try:
        pdf_file.seek(0)
        
        # Tabula needs a file path, so save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name
        
        try:
            # Extract all tables from all pages
            dfs = tabula.read_pdf(
                tmp_path,
                pages='all',
                multiple_tables=True,
                pandas_options={'header': 'infer'}
            )
            
            if dfs:
                tables = dfs
                metadata['total_tables'] = len(dfs)
                metadata['pages_processed'] = 'all'
                
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        pdf_file.seek(0)
        
    except Exception as e:
        metadata['errors'].append(f"Tabula error: {str(e)}")
    
    return tables, metadata


def extract_text_tables(pdf_file, method: str = 'pdfplumber') -> Tuple[List[pd.DataFrame], dict]:
    """
    Main extraction function for text-based PDFs with tables
    
    Args:
        pdf_file: Uploaded PDF file object
        method: Extraction method ('pdfplumber' or 'tabula')
        
    Returns:
        Tuple of (list of DataFrames, metadata dict)
    """
    
    if method == 'tabula':
        return extract_with_tabula(pdf_file)
    else:
        return extract_with_pdfplumber(pdf_file)


def combine_tables(tables: List[pd.DataFrame], method: str = 'vertical') -> pd.DataFrame:
    """
    Combine multiple tables into one DataFrame
    
    Args:
        tables: List of DataFrames
        method: 'vertical' (stack) or 'horizontal' (side by side)
        
    Returns:
        Combined DataFrame
    """
    if not tables:
        return pd.DataFrame()
    
    if len(tables) == 1:
        return tables[0]
    
    try:
        if method == 'vertical':
            # Stack tables vertically (concatenate rows)
            return pd.concat(tables, ignore_index=True)
        else:
            # Place tables side by side (concatenate columns)
            return pd.concat(tables, axis=1)
    except Exception as e:
        print(f"Error combining tables: {str(e)}")
        # Return first table if combination fails
        return tables[0]
