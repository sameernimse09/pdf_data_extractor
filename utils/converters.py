"""
Data conversion utilities
Convert extracted data to CSV or Excel formats
"""

import pandas as pd
from io import BytesIO
from typing import Union, List


def dataframe_to_csv(df: pd.DataFrame) -> bytes:
    """
    Convert pandas DataFrame to CSV bytes
    
    Args:
        df: pandas DataFrame
        
    Returns:
        CSV file as bytes
    """
    return df.to_csv(index=False).encode('utf-8')


def dataframe_to_excel(df: pd.DataFrame, sheet_name: str = 'Sheet1') -> bytes:
    """
    Convert pandas DataFrame to Excel bytes
    
    Args:
        df: pandas DataFrame
        sheet_name: Name for the Excel sheet
        
    Returns:
        Excel file as bytes
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()


def multiple_dataframes_to_excel(dataframes: List[pd.DataFrame], 
                                  sheet_names: List[str] = None) -> bytes:
    """
    Convert multiple DataFrames to a single Excel file with multiple sheets
    
    Args:
        dataframes: List of pandas DataFrames
        sheet_names: List of sheet names (optional)
        
    Returns:
        Excel file as bytes
    """
    if sheet_names is None:
        sheet_names = [f'Sheet{i+1}' for i in range(len(dataframes))]
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for df, sheet_name in zip(dataframes, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return output.getvalue()


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning operations on extracted data
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Remove completely empty rows and columns
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')
    
    # Strip whitespace from string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Replace 'None' strings with actual None
    df = df.replace('None', None)
    
    return df


def get_file_extension(format_type: str) -> str:
    """Get file extension for the given format"""
    extensions = {
        'csv': '.csv',
        'excel': '.xlsx'
    }
    return extensions.get(format_type.lower(), '.csv')


def get_mime_type(format_type: str) -> str:
    """Get MIME type for the given format"""
    mime_types = {
        'csv': 'text/csv',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    return mime_types.get(format_type.lower(), 'text/csv')
