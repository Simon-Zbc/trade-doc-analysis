"""Trade Document Analysis Streamlit Application"""

from gpt_analyzer import GPTAnalyzer
from document_analyzer import DocumentAnalyzer
from config import validate_config, DOCUMENT_TYPES
import streamlit as st
import logging
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))


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
if "uploaded_file_1" not in st.session_state:
    st.session_state.uploaded_file_1 = None
if "uploaded_file_2" not in st.session_state:
    st.session_state.uploaded_file_2 = None
if "analysis_result_1" not in st.session_state:
    st.session_state.analysis_result_1 = None
if "analysis_result_2" not in st.session_state:
    st.session_state.analysis_result_2 = None
if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None
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
            st.info(
                "Please ensure all required environment variables are set in .env file")
            st.stop()


def clear_analysis():
    """Clear uploaded files and analysis results"""
    st.session_state.uploaded_file_1 = None
    st.session_state.uploaded_file_2 = None
    st.session_state.analysis_result_1 = None
    st.session_state.analysis_result_2 = None
    st.session_state.comparison_result = None
    st.rerun()


def analyze_single_document(file, is_doc_1=True):
    """Analyze a single document"""
    try:
        # Read file content
        file_bytes = file.read()
        file_name = file.name

        # Step 1: Extract content using Document Intelligence
        logger.info(f"📋 Extracting content from {file_name}...")
        doc_analysis = st.session_state.document_analyzer.analyze_document(
            file_bytes, file_name
        )

        if doc_analysis["status"] == "error":
            return {"status": "error", "error_message": doc_analysis['error_message']}

        # Step 2: Analyze with GPT
        logger.info(f"🤖 Analyzing {file_name} with GPT...")
        gpt_result = st.session_state.gpt_analyzer.analyze_document(
            doc_analysis["extracted_text"],
            doc_analysis["tables"]
        )

        if gpt_result["status"] == "error":
            return {"status": "error", "error_message": gpt_result['error_message']}

        return gpt_result

    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return {"status": "error", "error_message": str(e)}


def analyze_documents():
    """Analyze both uploaded documents"""
    import time

    if st.session_state.uploaded_file_1 is None or st.session_state.uploaded_file_2 is None:
        st.warning("⚠️ Please upload both files first")
        return

    # Initialize comparison result
    st.session_state.comparison_result = None

    with st.spinner("🔄 Analyzing documents..."):
        # Analyze first document
        st.info("📋 Analyzing Document 1...")
        result_1 = analyze_single_document(
            st.session_state.uploaded_file_1, is_doc_1=True)

        if result_1["status"] == "error":
            st.error(
                f"❌ Document 1 analysis failed: {result_1['error_message']}")
            return

        # Analyze second document
        st.info("📋 Analyzing Document 2...")
        result_2 = analyze_single_document(
            st.session_state.uploaded_file_2, is_doc_1=False)

        if result_2["status"] == "error":
            st.error(
                f"❌ Document 2 analysis failed: {result_2['error_message']}")
            return

        # Store results
        st.session_state.analysis_result_1 = result_1
        st.session_state.analysis_result_2 = result_2

        logger.info("✅ Both documents analyzed successfully")

        # Add delay to ensure Document 2 analysis is fully processed
        logger.info("⏳ Waiting 1 second before comparison...")
        time.sleep(1)

        # Compare documents
        st.info("🔍 Comparing documents for discrepancies...")
        comparison = st.session_state.gpt_analyzer.compare_documents(
            result_1, result_2)

        if comparison["status"] == "error":
            st.error(f"❌ Comparison failed: {comparison['error_message']}")
            logger.error(f"Comparison error: {comparison['error_message']}")
        else:
            st.session_state.comparison_result = comparison["comparison_result"]
            st.success("✅ Analysis and comparison completed successfully!")
            logger.info("✅ Comparison completed successfully")

        st.rerun()


def display_comparison_results():
    """Display side-by-side comparison results"""
    if st.session_state.analysis_result_1 is None or st.session_state.analysis_result_2 is None:
        return

    result_1 = st.session_state.analysis_result_1
    result_2 = st.session_state.analysis_result_2

    # Document type header
    st.markdown("---")
    st.subheader("📑 Document Types")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Document 1:**")
        st.write(f"  Japanese: {result_1['document_type']['ja_name']}")
        st.write(f"  English: {result_1['document_type']['en_name']}")
    with col2:
        st.write(f"**Document 2:**")
        st.write(f"  Japanese: {result_2['document_type']['ja_name']}")
        st.write(f"  English: {result_2['document_type']['en_name']}")

    # Extracted information side-by-side
    st.markdown("---")
    st.subheader("📊 Extracted Information (Side-by-Side)")

    col1, col2 = st.columns(2)

    # Document 1 fields
    with col1:
        st.write("**Document 1 - Extracted Fields:**")
        fields_1 = result_1.get("detailed_information", {}).get("fields", {})
        if fields_1:
            for field_name, field_value in fields_1.items():
                st.text_input(
                    label=field_name,
                    value=str(field_value),
                    disabled=True,
                    key=f"doc1_field_{field_name}"
                )
        else:
            st.warning("⚠️ No fields extracted from Document 1")

    # Document 2 fields
    with col2:
        st.write("**Document 2 - Extracted Fields:**")
        fields_2 = result_2.get("detailed_information", {}).get("fields", {})
        if fields_2:
            for field_name, field_value in fields_2.items():
                st.text_input(
                    label=field_name,
                    value=str(field_value),
                    disabled=True,
                    key=f"doc2_field_{field_name}"
                )
        else:
            st.warning("⚠️ No fields extracted from Document 2")

    # Notes side-by-side
    st.markdown("---")
    st.subheader("📝 Summary Notes (Side-by-Side)")

    col1, col2 = st.columns(2)

    with col1:
        notes_1 = result_1.get("detailed_information", {}).get(
            "additional_notes", "No notes")
        st.info(f"**Document 1 Notes:**\n\n{notes_1}")

    with col2:
        notes_2 = result_2.get("detailed_information", {}).get(
            "additional_notes", "No notes")
        st.info(f"**Document 2 Notes:**\n\n{notes_2}")

    # Discrepancy check results
    st.markdown("---")
    st.subheader("🔍 Discrepancy Check Results")

    # Check if comparison was performed
    if st.session_state.comparison_result is None:
        st.warning(
            "⚠️ Comparison has not been completed or encountered an error. Please check the logs above.")
        return

    comparison = st.session_state.comparison_result

    # Matching items (green)
    st.write("**✅ Matching Items (Green):**")
    matching = comparison.get("matching_items", [])
    if matching:
        for item in matching:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success(f"{item.get('field1')}: {item.get('value1')}")
            with col2:
                st.write("=")
            with col3:
                st.success(f"{item.get('field2')}: {item.get('value2')}")
    else:
        st.write("No matching items found")

    st.write("")

    # Discrepant items (red)
    st.write("**❌ Discrepant Items (Red):**")
    discrepant = comparison.get("discrepant_items", [])
    if discrepant:
        for item in discrepant:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.error(f"{item.get('field1')}: {item.get('value1')}")
            with col2:
                st.write("≠")
            with col3:
                st.error(f"{item.get('field2')}: {item.get('value2')}")
            st.caption(f"Reason: {item.get('reason', 'Unknown')}")
    else:
        st.write("No discrepant items found")

    st.write("")

    # Items unique to each document
    st.write("**📋 Items Unique to Each Document:**")
    col1, col2 = st.columns(2)

    with col1:
        unique_1 = comparison.get("unique_to_doc1", [])
        if unique_1:
            st.write("**Unique to Document 1:**")
            for item in unique_1:
                st.warning(f"- {item.get('field')}: {item.get('value')}")
        else:
            st.write("No unique items")

    with col2:
        unique_2 = comparison.get("unique_to_doc2", [])
        if unique_2:
            st.write("**Unique to Document 2:**")
            for item in unique_2:
                st.warning(f"- {item.get('field')}: {item.get('value')}")
        else:
            st.write("No unique items")

    # Summary
    st.markdown("---")
    st.subheader("📌 Comparison Summary")
    summary = comparison.get("summary", "No summary available")
    st.info(summary)


def main():
    """Main application"""
    st.title("📄 Trade Document Analysis & Comparison System")
    st.markdown(
        "#### Analyze and compare two trade documents using Azure Document Intelligence & AI")

    # Initialize analyzers
    initialize_analyzers()

    # Top section: File upload and controls
    st.markdown("### Document Upload (2 Documents)")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Document 1:**")
        uploaded_file_1 = st.file_uploader(
            "Upload first trade document (PDF)",
            type=["pdf"],
            key="file_uploader_1"
        )
        if uploaded_file_1 is not None:
            st.session_state.uploaded_file_1 = uploaded_file_1
            st.success(f"✅ Uploaded: {uploaded_file_1.name}")

    with col2:
        st.write("**Document 2:**")
        uploaded_file_2 = st.file_uploader(
            "Upload second trade document (PDF)",
            type=["pdf"],
            key="file_uploader_2"
        )
        if uploaded_file_2 is not None:
            st.session_state.uploaded_file_2 = uploaded_file_2
            st.success(f"✅ Uploaded: {uploaded_file_2.name}")

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Analyze & Compare", use_container_width=True):
            analyze_documents()

    with col2:
        pass

    with col3:
        if st.button("🗑️ Clear All", use_container_width=True):
            clear_analysis()

    # Display results
    st.markdown("---")
    st.markdown("### Analysis & Comparison Results")

    if st.session_state.analysis_result_1 is not None and st.session_state.analysis_result_2 is not None:
        display_comparison_results()
    else:
        st.info(
            "📌 Upload two documents and click 'Analyze & Compare' to see results here")

    # Footer with supported document types
    with st.expander("ℹ️ Supported Document Types"):
        for doc_class, doc_info in DOCUMENT_TYPES.items():
            st.markdown(f"**{doc_info['ja_name']}** ({doc_info['en_name']})")
            st.caption(
                f"Extract fields: {', '.join(doc_info['extract_fields'][:3])}...")


if __name__ == "__main__":
    main()
