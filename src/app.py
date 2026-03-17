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
if "uploaded_lc" not in st.session_state:
    st.session_state.uploaded_lc = None
if "uploaded_other_files" not in st.session_state:
    st.session_state.uploaded_other_files = []
if "lc_analysis_result" not in st.session_state:
    st.session_state.lc_analysis_result = None
if "other_files_analysis_results" not in st.session_state:
    st.session_state.other_files_analysis_results = {}
if "discrepancy_check_result" not in st.session_state:
    st.session_state.discrepancy_check_result = None
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
    st.session_state.uploaded_lc = None
    st.session_state.uploaded_other_files = []
    st.session_state.lc_analysis_result = None
    st.session_state.other_files_analysis_results = {}
    st.session_state.discrepancy_check_result = None
    st.rerun()


def analyze_single_document(file, is_lc=False):
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
    """
    Analyze L/C and other documents, then check discrepancies

    Flow:
    1. Analyze L/C file (must be Letter of Credit)
    2. If not L/C, stop with error
    3. Analyze other files (Invoice, B/L, AWB, etc.)
    4. Run discrepancy check with L/C as reference
    """
    # import time

    # Validate inputs
    if st.session_state.uploaded_lc is None:
        st.error("❌ Please upload Letter of Credit (L/C) file first")
        return

    if len(st.session_state.uploaded_other_files) == 0:
        st.error("❌ Please upload at least one other document (Invoice, B/L, etc.)")
        return

    # Initialize results
    st.session_state.lc_analysis_result = None
    st.session_state.other_files_analysis_results = {}
    st.session_state.discrepancy_check_result = None

    with st.spinner("🔄 Analyzing documents..."):
        # ===== STEP 1: Analyze L/C file =====
        st.info("📋 Step 1: Analyzing Letter of Credit...")
        lc_result = analyze_single_document(
            st.session_state.uploaded_lc, is_lc=True)

        if lc_result["status"] == "error":
            st.error(f"❌ L/C analysis failed: {lc_result['error_message']}")
            return

        # Verify it's Letter of Credit
        lc_doc_class = lc_result.get("document_class", "").lower()
        if lc_doc_class != "letter_of_credit":
            st.error(
                f"❌ ERROR: Uploaded L/C file is not a Letter of Credit. Detected as: {lc_result.get('document_type', {}).get('ja_name', 'Unknown')}")
            logger.error(f"Expected letter_of_credit, got {lc_doc_class}")
            return

        st.session_state.lc_analysis_result = lc_result
        st.success(
            f"✅ L/C Analysis completed: {lc_result['document_type']['ja_name']}")
        logger.info(
            f"✅ L/C verified as {lc_result['document_type']['ja_name']}")

        # ===== STEP 2: Analyze other documents =====
        st.info("📋 Step 2: Analyzing other documents...")
        for idx, file in enumerate(st.session_state.uploaded_other_files, 1):
            st.info(
                f"   Analyzing document {idx}/{len(st.session_state.uploaded_other_files)}: {file.name}")

            other_result = analyze_single_document(file, is_lc=False)

            if other_result["status"] == "error":
                st.warning(
                    f"⚠️ Document {idx} ({file.name}) analysis failed: {other_result['error_message']}")
                continue

            doc_class = other_result.get("document_class", "").lower()
            st.session_state.other_files_analysis_results[doc_class] = other_result
            logger.info(
                f"✅ Document {idx} analyzed as: {other_result['document_type']['ja_name']}")

        if len(st.session_state.other_files_analysis_results) == 0:
            st.error("❌ No other documents could be analyzed successfully")
            return

        st.success(
            f"✅ Other documents analysis completed: {len(st.session_state.other_files_analysis_results)} documents")
        logger.info(
            f"✅ Completed analysis of {len(st.session_state.other_files_analysis_results)} other documents")

        # ===== STEP 3: Run discrepancy check =====
        # logger.info("⏳ Waiting 1 second before discrepancy check...")
        # time.sleep(1)

        st.info("🔍 Step 3: Running discrepancy check...")
        discrepancy_result = st.session_state.gpt_analyzer.check_discrepancies_with_lc(
            st.session_state.lc_analysis_result,
            st.session_state.other_files_analysis_results
        )

        if discrepancy_result["status"] == "error":
            st.error(
                f"❌ Discrepancy check failed: {discrepancy_result['error_message']}")
            logger.error(
                f"Discrepancy check error: {discrepancy_result['error_message']}")
        else:
            st.session_state.discrepancy_check_result = discrepancy_result["discrepancy_result"]
            st.success(
                "✅ Analysis and discrepancy check completed successfully!")
            logger.info("✅ Discrepancy check completed successfully")

        st.rerun()


def display_discrepancy_results():
    """Display discrepancy check results"""
    if st.session_state.lc_analysis_result is None:
        return

    lc_result = st.session_state.lc_analysis_result
    other_results = st.session_state.other_files_analysis_results

    # ===== L/C Information =====
    st.markdown("---")
    st.subheader("📑 Letter of Credit Information")

    st.write(
        f"**Document Type:** {lc_result['document_type']['ja_name']} ({lc_result['document_type']['en_name']})")

    lc_fields = lc_result.get("detailed_information", {}).get("fields", {})
    if lc_fields:
        col1, col2 = st.columns(2)
        fields_list = list(lc_fields.items())
        mid_point = len(fields_list) // 2

        with col1:
            for field_name, field_value in fields_list[:mid_point]:
                st.text_input(
                    label=field_name,
                    value=str(field_value),
                    disabled=True,
                    key=f"lc_field_{field_name}"
                )
        with col2:
            for field_name, field_value in fields_list[mid_point:]:
                st.text_input(
                    label=field_name,
                    value=str(field_value),
                    disabled=True,
                    key=f"lc_field_{field_name}"
                )

    # ===== Other Documents Information =====
    st.markdown("---")
    st.subheader("📊 Other Documents Information")

    if other_results:
        tabs = st.tabs(
            [f"📄 {result['document_type']['ja_name']}" for result in other_results.values()])

        for tab, (doc_class, result) in zip(tabs, other_results.items()):
            with tab:
                st.write(
                    f"**Type:** {result['document_type']['ja_name']} ({result['document_type']['en_name']})")

                fields = result.get("detailed_information",
                                    {}).get("fields", {})
                if fields:
                    col1, col2 = st.columns(2)
                    fields_list = list(fields.items())
                    mid_point = len(fields_list) // 2

                    with col1:
                        for field_name, field_value in fields_list[:mid_point]:
                            st.text_input(
                                label=field_name,
                                value=str(field_value),
                                disabled=True,
                                key=f"other_{doc_class}_{field_name}"
                            )
                    with col2:
                        for field_name, field_value in fields_list[mid_point:]:
                            st.text_input(
                                label=field_name,
                                value=str(field_value),
                                disabled=True,
                                key=f"other_{doc_class}_{field_name}"
                            )
    else:
        st.warning("⚠️ No other documents were successfully analyzed")

    # ===== Discrepancy Check Results =====
    st.markdown("---")
    st.subheader("🔍 Discrepancy Check Results (10 Key Items)")

    if st.session_state.discrepancy_check_result is None:
        st.warning(
            "⚠️ Discrepancy check has not been completed or encountered an error. Please check the logs above.")
        return

    check_result = st.session_state.discrepancy_check_result

    # Display each check item
    checks = check_result.get("checks", [])
    if checks:
        for check in checks:
            item_num = check.get("item_number", 0)
            item_name = check.get("item_name", "")
            status = check.get("status", "")
            severity = check.get("severity", "info")
            lc_value = check.get("lc_value", "N/A")
            other_value = check.get("other_value", "N/A")
            discrepancy = check.get("discrepancy", "No discrepancy")

            # Color-code based on status
            if status == "OK":
                st.success(f"✅ {item_num}. {item_name}")
            elif status == "NG":
                st.error(f"❌ {item_num}. {item_name}")
            else:
                st.warning(f"⚠️ {item_num}. {item_name}")

            # Display details
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"**L/C:** {lc_value}")
            with col2:
                st.caption(f"**Other Doc:** {other_value}")

            if discrepancy != "No discrepancy":
                st.caption(f"📌 {discrepancy}")
            st.write("")

    # Display critical issues
    st.markdown("---")
    st.subheader("⚠️ Critical Issues & Summary")

    critical_issues = check_result.get("critical_issues", [])
    if critical_issues:
        st.error("**Critical Issues Found:**")
        for issue in critical_issues:
            st.write(f"- ❌ {issue}")
    else:
        st.success("**No critical issues found**")

    # Display warnings
    warnings = check_result.get("warnings", [])
    if warnings:
        st.warning("**Warnings:**")
        for warning in warnings:
            st.write(f"- ⚠️ {warning}")

    # Display summary
    summary = check_result.get("summary", "No summary available")
    st.info(f"**Summary:** {summary}")

    # Display recommendations
    recommendations = check_result.get("recommendations", [])
    if recommendations:
        st.markdown("---")
        st.subheader("💡 Recommendations")
        for rec in recommendations:
            st.write(f"- 📌 {rec}")


def main():
    """Main application"""
    st.title("📄 Trade Document Analysis & L/C Discrepancy Check System")
    st.markdown(
        "#### Analyze Letter of Credit and related documents for discrepancies using Azure AI")

    # Initialize analyzers
    initialize_analyzers()

    # Top section: File upload and controls
    st.markdown("### Document Upload")

    col1, col2 = st.columns(2)

    # ===== LEFT: Letter of Credit (Single File) =====
    with col1:
        st.write("**Letter of Credit (L/C) - Single File:**")
        uploaded_lc = st.file_uploader(
            "Upload Letter of Credit (L/C) PDF only",
            type=["pdf"],
            key="file_uploader_lc"
        )
        if uploaded_lc is not None:
            st.session_state.uploaded_lc = uploaded_lc
            st.success(f"✅ Uploaded: {uploaded_lc.name}")

    # ===== RIGHT: Other Documents (Multiple Files) =====
    with col2:
        st.write("**Other Documents - Multiple Files:**")
        st.caption("(Invoice, Bill of Lading, Air Waybill, etc.)")
        uploaded_others = st.file_uploader(
            "Upload other trade documents (PDF)",
            type=["pdf"],
            accept_multiple_files=True,
            key="file_uploader_others"
        )
        if uploaded_others:
            st.session_state.uploaded_other_files = uploaded_others
            for file in uploaded_others:
                st.success(f"✅ Uploaded: {file.name}")

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Analyze & Check Discrepancies", use_container_width=True):
            analyze_documents()

    with col2:
        pass

    with col3:
        if st.button("🗑️ Clear All", use_container_width=True):
            clear_analysis()

    # Display results
    st.markdown("---")
    st.markdown("### Analysis & Discrepancy Check Results")

    if st.session_state.lc_analysis_result is not None:
        display_discrepancy_results()
    else:
        st.info(
            "📌 Upload L/C file and other documents, then click 'Analyze & Check Discrepancies' to see results here")

    # Footer with supported document types
    with st.expander("ℹ️ Supported Document Types"):
        for doc_class, doc_info in DOCUMENT_TYPES.items():
            if doc_class == "letter_of_credit":
                st.markdown(
                    f"**🔑 {doc_info['ja_name']}** ({doc_info['en_name']}) - Required as reference")
            else:
                st.markdown(
                    f"**{doc_info['ja_name']}** ({doc_info['en_name']})")
            st.caption(
                f"Extract fields: {', '.join(doc_info['extract_fields'][:3])}...")


if __name__ == "__main__":
    main()
