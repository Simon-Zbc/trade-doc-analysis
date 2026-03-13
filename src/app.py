"""Trade Document Analysis Streamlit Application"""

import streamlit as st
import logging
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import validate_config, DOCUMENT_TYPES
from document_analyzer import DocumentAnalyzer
from gpt_analyzer import GPTAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Trade Document Analysis",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "document_analyzer" not in st.session_state:
    st.session_state.document_analyzer = None
if "gpt_analyzer" not in st.session_state:
    st.session_state.gpt_analyzer = None

def initialize_analyzers():
    """Initialize analyzers if not already done"""
    if st.session_state.document_analyzer is None:
        try:
            validate_config()
            st.session_state.document_analyzer = DocumentAnalyzer()
            st.session_state.gpt_analyzer = GPTAnalyzer()
        except Exception as e:
            st.error(f"❌ Configuration Error: {str(e)}")
            st.info("Please ensure all required environment variables are set in .env file")
            st.stop()

def clear_analysis():
    """Clear uploaded file and analysis results"""
    st.session_state.uploaded_file = None
    st.session_state.analysis_result = None
    st.rerun()

def analyze_document():
    """Analyze the uploaded document"""
    if st.session_state.uploaded_file is None:
        st.warning("⚠️ Please upload a file first")
        return
    
    with st.spinner("🔄 Analyzing document..."):
        try:
            # Read file content
            file_bytes = st.session_state.uploaded_file.read()
            file_name = st.session_state.uploaded_file.name
            
            # Step 1: Extract content using Document Intelligence
            st.info("📋 Extracting document content...")
            doc_analysis = st.session_state.document_analyzer.analyze_document(
                file_bytes, file_name
            )
            
            if doc_analysis["status"] == "error":
                st.error(f"❌ Document extraction failed: {doc_analysis['error_message']}")
                return
            
            # Step 2: Analyze with GPT
            st.info("🤖 Analyzing with GPT...")
            gpt_result = st.session_state.gpt_analyzer.analyze_document(
                doc_analysis["extracted_text"],
                doc_analysis["tables"]
            )
            
            if gpt_result["status"] == "error":
                st.error(f"❌ GPT analysis failed: {gpt_result['error_message']}")
                return
            
            # Store result
            st.session_state.analysis_result = gpt_result
            st.success("✅ Analysis completed successfully!")
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            st.error(f"❌ Error during analysis: {str(e)}")

def display_results():
    """Display analysis results"""
    if st.session_state.analysis_result is None:
        return
    
    result = st.session_state.analysis_result
    
    # Display document type
    st.markdown("---")
    st.subheader("📑 Document Type")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Japanese:** {result['document_type']['ja_name']}")
    with col2:
        st.write(f"**English:** {result['document_type']['en_name']}")
    
    # Display extracted information
    st.subheader("📊 Extracted Information")
    
    if "detailed_information" in result:
        detailed_info = result["detailed_information"]
        
        if isinstance(detailed_info, dict):
            if "fields" in detailed_info:
                # Display fields in a formatted table
                fields_data = detailed_info.get("fields", {})
                
                # Create two columns for better layout
                cols = st.columns(2)
                col_idx = 0
                
                for field_name, field_value in fields_data.items():
                    with cols[col_idx % 2]:
                        st.text_input(
                            label=field_name,
                            value=str(field_value),
                            disabled=True,
                            key=f"field_{field_name}"
                        )
                    col_idx += 1
            
            # Display additional notes if present
            if "additional_notes" in detailed_info:
                st.subheader("📝 Notes")
                st.info(detailed_info["additional_notes"])
        else:
            st.write(detailed_info)
    else:
        st.write("No detailed information extracted")

def main():
    """Main application"""
    st.title("📄 Trade Document Analysis System")
    st.markdown("#### Analyze trade documents using Azure Document Intelligence & AI")
    
    # Initialize analyzers
    initialize_analyzers()
    
    # Top section: File upload and controls (sticky)
    st.markdown("### Document Upload")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a trade document (PDF)",
            type=["pdf"],
            key="file_uploader"
        )
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
    
    with col2:
        if st.button("🔍 Analyze", use_container_width=True):
            analyze_document()
    
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            clear_analysis()
    
    # Display file info if uploaded
    if st.session_state.uploaded_file is not None:
        st.success(f"✅ File uploaded: {st.session_state.uploaded_file.name}")
    
    # Scrollable result section
    st.markdown("---")
    st.markdown("### Analysis Results")
    
    if st.session_state.analysis_result is not None:
        display_results()
    else:
        st.info("📌 Upload a document and click 'Analyze' to see results here")
    
    # Footer with supported document types
    with st.expander("ℹ️ Supported Document Types"):
        for doc_class, doc_info in DOCUMENT_TYPES.items():
            st.markdown(f"**{doc_info['ja_name']}** ({doc_info['en_name']})")
            st.caption(f"Extract fields: {', '.join(doc_info['extract_fields'][:3])}...")

if __name__ == "__main__":
    main()
