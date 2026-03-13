"""Azure Document Intelligence Document Analyzer"""

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from config import DOCUMENT_INTELLIGENCE_ENDPOINT, DOCUMENT_INTELLIGENCE_KEY
import logging

logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """Analyzes documents using Azure Document Intelligence"""

    def __init__(self):
        """Initialize Document Intelligence client"""
        self.client = DocumentIntelligenceClient(
            endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY)
        )

    def analyze_document(self, file_bytes: bytes, file_name: str) -> dict:
        """
        Analyze a document using the Layout model

        Args:
            file_bytes: PDF file content as bytes
            file_name: Name of the file

        Returns:
            Dictionary containing extracted text and structured data
        """
        try:
            logger.info(f"Starting document analysis for {file_name}")

            # Analyze the document using the Layout model
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-layout",
                body=file_bytes,
                content_type="application/pdf"
            )

            result = poller.result()

            # Extract text content
            extracted_text = ""
            if result.content:
                extracted_text = result.content

            # Extract tables if present
            tables_data = []
            if result.tables:
                for table_idx, table in enumerate(result.tables):
                    table_content = self._extract_table_data(table)
                    tables_data.append({
                        "table_index": table_idx,
                        "content": table_content
                    })

            logger.info(f"Document analysis completed for {file_name}")
            logger.info(
                f"✅ Extracted pages: {len(result.pages) if result.pages else 0}")
            logger.info(f"✅ Extracted tables: {len(tables_data)}")
            logger.info(f"✅ Text length: {len(extracted_text)} characters")

            result_dict = {
                "status": "success",
                "file_name": file_name,
                "extracted_text": extracted_text,
                "tables": tables_data,
                "page_count": len(result.pages) if result.pages else 0
            }

            # Log the result summary
            logger.info(f"📋 Document Analysis Result: {result_dict}")

            return result_dict

        except Exception as e:
            logger.error(f"Error analyzing document {file_name}: {str(e)}")
            return {
                "status": "error",
                "file_name": file_name,
                "error_message": str(e)
            }

    def _extract_table_data(self, table) -> list:
        """Extract table data into a structured format"""
        table_content = []
        cells = sorted(table.cells, key=lambda cell: (
            cell.row_index, cell.column_index))

        for cell in cells:
            table_content.append({
                "row": cell.row_index,
                "column": cell.column_index,
                "content": cell.content
            })

        return table_content
