"""Azure OpenAI GPT Analyzer for Document Classification and Extraction"""

import json
import logging
import os
from typing import Dict, Any
from openai import OpenAI
from config import (
    AZURE_AI_FOUNDRY_ENDPOINT,
    AZURE_AI_FOUNDRY_API_KEY,
    AZURE_AI_FOUNDRY_MODEL,
    DOCUMENT_TYPES
)

logger = logging.getLogger(__name__)


class GPTAnalyzer:
    """Analyzes documents using Azure OpenAI GPT models"""

    def __init__(self):
        """Initialize GPT Analyzer with Azure OpenAI client"""
        self.endpoint = AZURE_AI_FOUNDRY_ENDPOINT
        self.api_key = AZURE_AI_FOUNDRY_API_KEY
        self.model = AZURE_AI_FOUNDRY_MODEL

        # Initialize Azure OpenAI client using OpenAI SDK
        logger.info(f"🔐 Initializing Azure OpenAI client")
        logger.debug(f"Endpoint: {self.endpoint}")
        logger.debug(f"Model: {self.model}")

        # Construct base_url for Azure OpenAI endpoint
        # Format: https://{resource-name}.openai.azure.com/openai/v1/
        base_url = self.endpoint.rstrip('/')
        if not base_url.endswith('/openai/v1'):
            if base_url.endswith('.openai.azure.com'):
                base_url = f"{base_url}/openai/v1/"
            else:
                base_url = f"{base_url}/openai/v1/"

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )

    def analyze_document(self, extracted_text: str, tables_data: list) -> Dict[str, Any]:
        """
        Two-step analysis: First classify document type, then extract details

        Args:
            extracted_text: Text extracted from document
            tables_data: Structured table data from document

        Returns:
            Dictionary containing document type and extracted information
        """
        try:
            # Step 1: Classify document type
            document_type = self._classify_document_type(
                extracted_text, tables_data)

            if document_type["status"] == "error":
                return document_type

            # Step 2: Extract detailed information based on document type
            document_class = document_type["document_class"]
            detailed_info = self._extract_detailed_info(
                extracted_text,
                tables_data,
                document_class
            )

            return {
                "status": "success",
                "document_type": document_type["document_type"],
                "document_class": document_class,
                "detailed_information": detailed_info
            }

        except Exception as e:
            logger.error(f"❌ Error in GPT analysis: {str(e)}")
            logger.debug(
                f"Exception details: {type(e).__name__}", exc_info=True)
            return {
                "status": "error",
                "error_message": str(e)
            }

    def _classify_document_type(self, extracted_text: str, tables_data: list) -> Dict[str, Any]:
        """
        Classify the document type using GPT

        Args:
            extracted_text: Extracted text content
            tables_data: Table data from document

        Returns:
            Dictionary with document type classification
        """
        try:
            logger.info("🔍 Classifying document type...")

            # Prepare prompt for classification
            document_types_list = "\n".join([
                f"- {info['ja_name']} ({info['en_name']})"
                for info in DOCUMENT_TYPES.values()
            ])

            prompt = f"""以下の貿易書類のテキストを分析して、書類の種類を判別してください。

書類の種類は以下から選択してください：
{document_types_list}

抽出されたテキスト：
{extracted_text[:2000]}

テーブルデータ：
{json.dumps(tables_data[:3], ensure_ascii=False) if tables_data else "None"}

JSON形式で以下の情報を返してください：
{{
    "document_class": "判別した書類の英語クラス名（invoice, bill_of_lading, air_waybill, insurance_policy, bill_of_exchange, letter_of_credit）",
    "confidence": "確信度（0-100）",
    "reason": "判別の理由"
}}
"""

            response = self._call_gpt(prompt)

            logger.debug(f"Classification response: {response}")

            # Parse response - handle potential markdown formatting
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text)
            document_class = result.get("document_class", "").lower()

            # Validate document class
            if document_class not in DOCUMENT_TYPES:
                logger.warning(f"⚠️  Unknown document class: {document_class}")
                return {
                    "status": "error",
                    "error_message": f"Unknown document class: {document_class}"
                }

            document_info = DOCUMENT_TYPES[document_class]
            logger.info(
                f"✅ Document classified as: {document_info['ja_name']} ({document_info['en_name']})")
            logger.info(f"   Confidence: {result.get('confidence', 0)}%")

            return {
                "status": "success",
                "document_class": document_class,
                "document_type": {
                    "ja_name": document_info["ja_name"],
                    "en_name": document_info["en_name"]
                },
                "confidence": result.get("confidence", 0),
                "reason": result.get("reason", "")
            }

        except Exception as e:
            logger.error(f"❌ Error classifying document: {str(e)}")
            logger.debug(
                f"Exception details: {type(e).__name__}", exc_info=True)
            return {
                "status": "error",
                "error_message": f"Classification failed: {str(e)}"
            }

    def _extract_detailed_info(self, extracted_text: str, tables_data: list, document_class: str) -> Dict[str, Any]:
        """
        Extract detailed information based on document type

        Args:
            extracted_text: Extracted text content
            tables_data: Table data from document
            document_class: Classified document type

        Returns:
            Dictionary with extracted detailed information
        """
        try:
            logger.info(
                f"📝 Extracting detailed information for {document_class}...")

            document_info = DOCUMENT_TYPES.get(document_class, {})
            extract_fields = document_info.get("extract_fields", [])
            fields_str = ", ".join(extract_fields)

            prompt = f"""以下の{document_info.get('ja_name', 'document')}から、以下の情報を抽出してください：

抽出対象項目: {fields_str}

抽出されたテキスト：
{extracted_text[:3000]}

テーブルデータ：
{json.dumps(tables_data[:5], ensure_ascii=False) if tables_data else "None"}

JSON形式で以下の構造で返してください：
{{
    "fields": {{
        "field_name": "extracted_value",
        ...
    }},
    "additional_notes": "追加情報や備考"
}}

見つからない情報は、値を"N/A"として返してください。
"""

            response = self._call_gpt(prompt)

            logger.debug(f"Extraction response: {response}")

            # Parse response - handle potential markdown formatting
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            result = json.loads(response_text)
            logger.info(f"✅ Information extraction completed")
            logger.info(
                f"   Fields extracted: {len(result.get('fields', {}))} items")

            return result

        except Exception as e:
            logger.error(f"❌ Error extracting detailed info: {str(e)}")
            logger.debug(
                f"Exception details: {type(e).__name__}", exc_info=True)
            return {
                "status": "error",
                "error_message": f"Extraction failed: {str(e)}"
            }

    def _call_gpt(self, prompt: str) -> str:
        """
        Call Azure OpenAI GPT API using OpenAI SDK

        Args:
            prompt: The prompt to send to GPT

        Returns:
            Response text from GPT
        """
        try:
            logger.info(f"💬 Calling GPT API with model: {self.model}")
            logger.debug(f"Prompt length: {len(prompt)} characters")

            # Call Azure OpenAI using the SDK
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that analyzes trade documents. Always respond in valid JSON format only, without any markdown formatting or code blocks."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=2000
            )

            logger.info(f"✅ GPT API Response received")
            logger.debug(
                f"Response tokens used: {response.usage.total_tokens}")

            # Extract response text
            response_text = response.choices[0].message.content
            logger.debug(f"Response preview: {response_text[:100]}...")

            return response_text

        except Exception as e:
            logger.error(f"❌ Error calling GPT API: {str(e)}")
            logger.debug(
                f"Exception details: {type(e).__name__}", exc_info=True)
            raise
