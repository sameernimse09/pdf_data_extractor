"""
Report/Document Extractor
Extracts text and any tables from report-style PDFs using pdfplumber
"""

import pdfplumber
import pandas as pd
from typing import List, Tuple, Dict


def extract_report_content(pdf_file) -> Tuple[Dict[str, any], dict]:
    """
    Extract all content (text + tables) from a report-style PDF
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        Tuple of (content dict, metadata dict)
    """
    
    content = {
        'full_text': [],
        'tables': [],
        'page_contents': []
    }
    
    metadata = {
        'method': 'pdfplumber comprehensive',
        'total_pages': 0,
        'total_tables': 0,
        'total_text_length': 0,
        'errors': []
    }
    
    try:
        pdf_file.seek(0)
        
        with pdfplumber.open(pdf_file) as pdf:
            metadata['total_pages'] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_content = {
                    'page_number': page_num,
                    'text': '',
                    'tables': []
                }
                
                try:
                    # Extract text
                    text = page.extract_text()
                    if text:
                        page_content['text'] = text
                        content['full_text'].append(f"--- Page {page_num} ---\n{text}\n")
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            if table and len(table) > 0:
                                # Convert to DataFrame
                                df = pd.DataFrame(table[1:], columns=table[0])
                                df.attrs['page'] = page_num
                                df.attrs['table_index'] = table_idx + 1
                                
                                page_content['tables'].append(df)
                                content['tables'].append(df)
                                
                except Exception as e:
                    metadata['errors'].append(f"Page {page_num}: {str(e)}")
                
                content['page_contents'].append(page_content)
            
            # Compile metadata
            metadata['total_tables'] = len(content['tables'])
            full_text_combined = "\n".join(content['full_text'])
            metadata['total_text_length'] = len(full_text_combined)
        
        pdf_file.seek(0)
        
    except Exception as e:
        metadata['errors'].append(f"General error: {str(e)}")
        pdf_file.seek(0)
    
    return content, metadata


def content_to_dataframe(content: Dict[str, any], include_text: bool = True) -> pd.DataFrame:
    """
    Convert extracted content to a single DataFrame
    
    Args:
        content: Content dictionary from extract_report_content
        include_text: Whether to include text content in output
        
    Returns:
        Combined DataFrame
    """
    
    rows = []
    
    # If there are tables, prioritize those
    if content['tables']:
        # Combine all tables
        for table in content['tables']:
            # Add page info as a column if available
            if hasattr(table, 'attrs') and 'page' in table.attrs:
                table_with_page = table.copy()
                table_with_page.insert(0, 'Source_Page', table.attrs['page'])
                rows.append(table_with_page)
            else:
                rows.append(table)
        
        # Concatenate all tables
        if rows:
            try:
                df = pd.concat(rows, ignore_index=True)
            except Exception:
                # If tables have different structures, keep them separate
                df = pd.DataFrame({
                    'Note': ['Multiple tables with different structures found'],
                    'Tables_Count': [len(rows)]
                })
        else:
            df = pd.DataFrame({'Message': ['No tables extracted']})
    
    # If no tables or user wants text
    elif include_text and content['full_text']:
        # Create DataFrame from text
        text_by_page = []
        for page_content in content['page_contents']:
            if page_content['text']:
                text_by_page.append({
                    'Page': page_content['page_number'],
                    'Content': page_content['text']
                })
        
        if text_by_page:
            df = pd.DataFrame(text_by_page)
        else:
            df = pd.DataFrame({'Message': ['No content extracted']})
    
    else:
        df = pd.DataFrame({'Message': ['No content extracted']})
    
    return df


def extract_report(pdf_file, output_type: str = 'combined') -> Tuple[pd.DataFrame, dict]:
    """
    Main extraction function for report-style PDFs
    
    Args:
        pdf_file: Uploaded PDF file object
        output_type: 'combined' (all in one), 'tables_only', or 'text_only'
        
    Returns:
        Tuple of (DataFrame, metadata dict)
    """
    
    # Extract all content
    content, metadata = extract_report_content(pdf_file)
    metadata['output_type'] = output_type
    
    # Convert to DataFrame based on output type
    if output_type == 'tables_only':
        df = content_to_dataframe(content, include_text=False)
    elif output_type == 'text_only':
        # Text only
        if content['full_text']:
            text_combined = "\n".join(content['full_text'])
            lines = [line for line in text_combined.split('\n') if line.strip()]
            df = pd.DataFrame({'Text': lines if lines else ['No text extracted']})
        else:
            df = pd.DataFrame({'Message': ['No text extracted']})
    else:  # combined
        df = content_to_dataframe(content, include_text=True)
    
    return df, metadata


def get_report_summary(content: Dict[str, any]) -> Dict[str, any]:
    """
    Get a summary of the report content
    
    Args:
        content: Content dictionary from extract_report_content
        
    Returns:
        Summary dictionary
    """
    
    summary = {
        'total_pages': len(content['page_contents']),
        'pages_with_text': sum(1 for p in content['page_contents'] if p['text']),
        'pages_with_tables': sum(1 for p in content['page_contents'] if p['tables']),
        'total_tables': len(content['tables']),
        'estimated_word_count': sum(len(text.split()) for text in content['full_text'])
    }
    
    return summary
