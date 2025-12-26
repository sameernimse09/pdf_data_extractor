"""
PDF Data Extractor - Main Streamlit Application
A smart PDF extraction tool with auto-detection and multiple extraction methods
"""

import streamlit as st
import pandas as pd
from io import BytesIO

# Import our custom modules
from utils.detector import detect_pdf_type, get_pdf_type_description, get_extraction_method_info
from utils.converters import (
    dataframe_to_csv, 
    dataframe_to_excel, 
    clean_dataframe,
    get_file_extension,
    get_mime_type
)
from extractors.text_table import extract_text_tables, combine_tables
from extractors.scanned import extract_scanned_pdf
from extractors.report import extract_report


# Page configuration
st.set_page_config(
    page_title="PDF Data Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application function"""
    
    # Header
    st.markdown('<p class="main-header">📄 PDF Data Extractor</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligently extract data from any PDF - tables, text, or scanned documents</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.markdown("---")
        st.markdown("### 📖 How to Use")
        st.markdown("""
        1. Upload your PDF file
        2. Review auto-detected type (or override)
        3. Choose extraction options
        4. Preview and download results
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Supported PDF Types")
        st.markdown("""
        - **Text-based with tables**: Digital PDFs with structured tables
        - **Scanned/Image-based**: PDFs from scanners (uses OCR)
        - **Reports/Documents**: Mixed content PDFs
        """)
        
        st.markdown("---")
        st.info("💡 **Tip**: For best results with scanned PDFs, ensure images are clear and high-resolution.")
    
    # Initialize session state
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = None
    if 'metadata' not in st.session_state:
        st.session_state.metadata = None
    if 'pdf_type' not in st.session_state:
        st.session_state.pdf_type = None
    
    # File upload
    st.header("1️⃣ Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload any PDF file - we'll auto-detect its type"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("File Type", "PDF")
        
        st.markdown("---")
        
        # Auto-detect PDF type
        st.header("2️⃣ PDF Type Detection")
        
        with st.spinner("🔍 Analyzing PDF..."):
            detected_type, detection_metadata = detect_pdf_type(uploaded_file)
            st.session_state.pdf_type = detected_type
        
        # Show detection results
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success(f"**Detected Type**: {get_pdf_type_description(detected_type)}")
            st.caption(get_extraction_method_info(detected_type))
            
            # Show detection details in expander
            with st.expander("📊 View Detection Details"):
                st.json(detection_metadata)
        
        with col2:
            st.metric("Detection Accuracy", detection_metadata.get('confidence', 'unknown').upper())
            st.metric("Pages", detection_metadata.get('total_pages', 'N/A'))
        
        # Allow user to override
        st.markdown("#### Override Detection (Optional)")
        pdf_type_override = st.selectbox(
            "Select PDF type manually if auto-detection is incorrect:",
            options=['auto', 'text_tables', 'scanned', 'report'],
            format_func=lambda x: 'Use Auto-Detection' if x == 'auto' else get_pdf_type_description(x),
            index=0
        )
        
        # Determine final PDF type
        final_pdf_type = detected_type if pdf_type_override == 'auto' else pdf_type_override
        
        if pdf_type_override != 'auto':
            st.info(f"Using manual selection: {get_pdf_type_description(final_pdf_type)}")
        
        st.markdown("---")
        
        # Extraction options based on PDF type
        st.header("3️⃣ Extraction Options")
        
        extraction_options = {}
        
        if final_pdf_type == 'text_tables':
            col1, col2 = st.columns(2)
            with col1:
                extraction_options['method'] = st.radio(
                    "Extraction Method",
                    options=['pdfplumber', 'tabula'],
                    help="pdfplumber is more flexible, tabula is specialized for tables"
                )
            with col2:
                extraction_options['combine'] = st.checkbox(
                    "Combine all tables into one",
                    value=True,
                    help="Stack all extracted tables vertically"
                )
        
        elif final_pdf_type == 'scanned':
            col1, col2 = st.columns(2)
            with col1:
                extraction_options['output_format'] = st.radio(
                    "Output Format",
                    options=['auto', 'text'],
                    help="Auto tries to detect structure, text returns simple text"
                )
            with col2:
                st.info("⚠️ OCR may take longer for large files")
        
        elif final_pdf_type == 'report':
            extraction_options['output_type'] = st.radio(
                "What to extract",
                options=['combined', 'tables_only', 'text_only'],
                help="Choose what content to extract from the report"
            )
        
        # Extract button
        if st.button("🚀 Extract Data", type="primary", use_container_width=True):
            with st.spinner(f"Extracting data using {final_pdf_type} method..."):
                try:
                    # Perform extraction based on PDF type
                    if final_pdf_type == 'text_tables':
                        tables, metadata = extract_text_tables(
                            uploaded_file, 
                            method=extraction_options.get('method', 'pdfplumber')
                        )
                        
                        if tables and extraction_options.get('combine', True):
                            df = combine_tables(tables)
                        elif tables:
                            df = tables[0]  # Use first table
                        else:
                            df = pd.DataFrame({'Message': ['No tables found']})
                        
                    elif final_pdf_type == 'scanned':
                        df, metadata = extract_scanned_pdf(
                            uploaded_file,
                            output_format=extraction_options.get('output_format', 'auto')
                        )
                        
                    else:  # report
                        df, metadata = extract_report(
                            uploaded_file,
                            output_type=extraction_options.get('output_type', 'combined')
                        )
                    
                    # Clean the data
                    df = clean_dataframe(df)
                    
                    # Store in session state
                    st.session_state.extracted_data = df
                    st.session_state.metadata = metadata
                    
                    st.success("✅ Extraction completed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Extraction failed: {str(e)}")
                    st.session_state.extracted_data = None
        
        # Show results if data was extracted
        if st.session_state.extracted_data is not None:
            st.markdown("---")
            st.header("4️⃣ Preview & Download")
            
            df = st.session_state.extracted_data
            metadata = st.session_state.metadata
            
            # Show metadata
            with st.expander("📋 Extraction Metadata"):
                st.json(metadata)
            
            # Show preview
            st.subheader("📊 Data Preview")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Method", metadata.get('method', 'N/A'))
            
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download section
            st.subheader("💾 Download Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV download
                csv_data = dataframe_to_csv(df)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_extracted.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Excel download
                excel_data = dataframe_to_excel(df)
                st.download_button(
                    label="📥 Download as Excel",
                    data=excel_data,
                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_extracted.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            # Additional info
            if metadata.get('errors'):
                with st.expander("⚠️ Warnings/Errors During Extraction"):
                    for error in metadata['errors']:
                        st.warning(error)
    
    else:
        # Landing page when no file is uploaded
        st.info("👆 Upload a PDF file to get started")
        
        # Example use cases
        st.markdown("---")
        st.header("💡 Example Use Cases")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📊 Financial Reports")
            st.markdown("Extract tables from quarterly reports, balance sheets, and financial statements")
        
        with col2:
            st.markdown("### 📄 Scanned Documents")
            st.markdown("Convert scanned invoices, receipts, and forms to editable data")
        
        with col3:
            st.markdown("### 📈 Research Papers")
            st.markdown("Extract data tables from academic papers and research documents")


if __name__ == "__main__":
    main()
