"""Azure OpenAI GPT Analyzer for Document Classification and Extraction"""

import json
import logging
import os
import time
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

            logger.info("⏳ Waiting 1 second before GPT classification call...")
            time.sleep(1)
            response = self._call_gpt(prompt)
            # time.sleep(1)
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

            logger.info("⏳ Waiting 1 second before GPT extraction call...")
            time.sleep(1)
            response = self._call_gpt(prompt)
            # time.sleep(1)
            logger.debug(f"Extraction response: {response}")

            # Parse response - handle potential markdown formatting more robustly
            response_text = response.strip()

            # Remove markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:].strip()

            if response_text.endswith('```'):
                response_text = response_text[:-3].strip()

            # Remove any remaining whitespace
            response_text = response_text.strip()

            # Check if response is empty
            if not response_text:
                logger.error("Empty response from GPT API")
                return {
                    "fields": {},
                    "additional_notes": "No information could be extracted"
                }

            logger.debug(f"Cleaned response text: {response_text[:200]}...")

            result = json.loads(response_text)
            logger.info(f"✅ Information extraction completed")
            logger.info(
                f"   Fields extracted: {len(result.get('fields', {}))} items")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing JSON: {str(e)}")
            logger.debug(f"Failed to parse: {response_text[:500]}")
            return {
                "fields": {},
                "additional_notes": "Failed to parse extracted information"
            }
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
            logger.debug(f"Prompt: {prompt}")

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
                ]
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

    def compare_documents(self, doc1_analysis: Dict[str, Any], doc2_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two document analyses for discrepancies

        Args:
            doc1_analysis: First document analysis result
            doc2_analysis: Second document analysis result

        Returns:
            Dictionary containing comparison results with matching and discrepant items
        """
        try:
            logger.info("🔍 Comparing two documents for discrepancies...")

            # Extract document information
            doc1_type = doc1_analysis.get(
                "document_type", {}).get("ja_name", "Unknown")
            doc1_fields = doc1_analysis.get(
                "detailed_information", {}).get("fields", {})

            doc2_type = doc2_analysis.get(
                "document_type", {}).get("ja_name", "Unknown")
            doc2_fields = doc2_analysis.get(
                "detailed_information", {}).get("fields", {})

            # Prepare comparison prompt
            prompt = f"""以下の2つの貿易書類の分析結果を比較してください。
同じ意味の項目であっても、フィールド名が異なる可能性があります。書類の内容を理解した上で比較してください。

**書類1（{doc1_type}）の抽出結果:**
```json
{json.dumps(doc1_fields, ensure_ascii=False, indent=2)}
```

**書類2（{doc2_type}）の抽出結果:**
```json
{json.dumps(doc2_fields, ensure_ascii=False, indent=2)}
```

以下のJSON形式で、ディスクレプスキー（相違点分析）結果を返してください：

{{
    "matching_items": [
        {{
            "field1": "フィールド名",
            "field2": "フィールド名",
            "value1": "値",
            "value2": "値",
            "status": "identical" または "semantically_equivalent"
        }}
    ],
    "discrepant_items": [
        {{
            "field1": "フィールド名",
            "field2": "フィールド名",
            "value1": "値",
            "value2": "値",
            "reason": "相違の理由"
        }}
    ],
    "unique_to_doc1": [
        {{
            "field": "フィールド名",
            "value": "値"
        }}
    ],
    "unique_to_doc2": [
        {{
            "field": "フィールド名",
            "value": "値"
        }}
    ],
    "summary": "全体的な相違点の要約と注釈"
}}

有効なJSON形式のみを返してください。マークダウンのコードブロックや説明は含めないでください。
"""

            # Log the prompt for debugging
            logger.info("📝 Comparison prompt:")
            logger.info(
                f"Document 1 type: {doc1_type}, Fields: {len(doc1_fields)}")
            logger.info(
                f"Document 2 type: {doc2_type}, Fields: {len(doc2_fields)}")
            logger.debug(f"Full prompt length: {len(prompt)} characters")
            logger.debug(f"Prompt content:\n{prompt[:500]}...")

            logger.info("⏳ Waiting 1 second before GPT comparison call...")
            time.sleep(1)
            response = self._call_gpt(prompt)
            # time.sleep(1)
            logger.debug(f"Comparison response: {response}")

            # Parse response - handle potential markdown formatting more robustly
            response_text = response.strip()

            # Remove markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:].strip()

            if response_text.endswith('```'):
                response_text = response_text[:-3].strip()

            # Remove any remaining whitespace
            response_text = response_text.strip()

            # Check if response is empty
            if not response_text:
                logger.error("Empty response from GPT API for comparison")
                return {
                    "status": "error",
                    "error_message": "No comparison result received from GPT"
                }

            logger.debug(
                f"Cleaned comparison response: {response_text[:200]}...")

            result = json.loads(response_text)
            logger.info(f"✅ Document comparison completed")

            return {
                "status": "success",
                "comparison_result": result
            }

        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing comparison JSON: {str(e)}")
            logger.debug(f"Failed to parse: {response_text[:500]}")
            return {
                "status": "error",
                "error_message": f"Failed to parse comparison result: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Error comparing documents: {str(e)}")
            logger.debug(
                f"Exception details: {type(e).__name__}", exc_info=True)
            return {
                "status": "error",
                "error_message": f"Comparison failed: {str(e)}"
            }

    def check_discrepancies_with_lc(self, lc_analysis: Dict[str, Any], other_files_analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check discrepancies between Letter of Credit and other documents

        Checks 10 key items:
        1. 船積日 (Shipment Date) - Check with Bill of Lading
        2. L/C有効期限 (L/C Validity)
        3. 呈示期限 (Presentation Period) - Check with Bill of Lading
        4. 要求書類の不備 (Required Documents) - Check Invoice, B/L document count
        5. 建値 (Price Terms) - Invoice FOB/CFR vs B/L FREIGHT PREPAID/COLLECT
        6. 船積地・荷揚地 (Ports)
        7. 商品 (Goods) - Check with B/L and Invoice
        8. 対外決済方法 (Settlement Method) vs SWIFT ADDRESS
        9. 手数料負担区分 (Commission split), P/O, S/A, A/A requirements
        10. ユーザンス期日 (Usance Period)

        Args:
            lc_analysis: Letter of Credit analysis result
            other_files_analyses: Dictionary of other document analyses {doc_type: analysis}

        Returns:
            Dictionary containing discrepancy check results
        """
        try:
            logger.info(
                "🔍 Checking discrepancies with Letter of Credit as reference...")

            # Extract L/C fields
            lc_fields = lc_analysis.get(
                "detailed_information", {}).get("fields", {})

            # Extract other documents' fields
            bl_analysis = other_files_analyses.get("bill_of_lading", {})
            invoice_analysis = other_files_analyses.get("invoice", {})

            bl_fields = bl_analysis.get(
                "detailed_information", {}).get("fields", {})
            invoice_fields = invoice_analysis.get(
                "detailed_information", {}).get("fields", {})

            # Prepare discrepancy check prompt with all relevant information
            prompt = f"""以下の信用状(Letter of Credit)と関連する貿易書類（船荷証券、インボイス等）に基づいて、
以下の10項目のディスクレパンシーチェックを行ってください。

**信用状(L/C)の抽出結果:**
```json
{json.dumps(lc_fields, ensure_ascii=False, indent=2)}
```

**船荷証券(Bill of Lading)の抽出結果:**
```json
{json.dumps(bl_fields, ensure_ascii=False, indent=2)}
```

**インボイス(Invoice)の抽出結果:**
```json
{json.dumps(invoice_fields, ensure_ascii=False, indent=2)}
```

以下の10項目について詳細にチェックし、JSON形式で結果を返してください：

1. **船積日チェック**: L/C船積期限 vs B/L船積日
2. **L/C有効期限**: 有効期限内か確認
3. **呈示期限チェック**: L/C呈示期間 vs B/L発行日
4. **要求書類の不備**: 要求通数とInvoice、B/Lの通数確認
5. **建値チェック**: Invoice(FOB/CFR) vs B/L(FREIGHT PREPAID/COLLECT)の対応
6. **船積地・荷揚地**: L/C記載地と実際の一致確認
7. **商品チェック**: L/C商品 vs B/L商品 vs Invoice商品の一致
8. **決済方法**: L/C対外決済方法とSWIFTアドレス（仕向銀行・中継銀行）確認
9. **手数料・条件**: 手数料負担区分、P/O、S/A、A/A要否確認
10. **ユーザンス期日**: ユーザンス期日の確認

以下のJSON形式で結果を返してください：

{{
    "checks": [
        {{
            "item_number": 1,
            "item_name": "船積日チェック",
            "status": "OK" または "NG" または "警告",
            "lc_value": "L/C値",
            "other_value": "他の書類の値",
            "discrepancy": "相違内容",
            "severity": "critical" または "warning" または "info"
        }},
        ...（全10項目）
    ],
    "summary": "全体的な評価と主要な問題点",
    "critical_issues": ["重大な問題のリスト"],
    "warnings": ["注意事項のリスト"],
    "recommendations": ["推奨事項のリスト"]
}}

有効なJSON形式のみを返してください。マークダウンのコードブロックや説明は含めないでください。
"""

            # Log the prompt
            logger.info("📝 Discrepancy check prompt prepared")
            logger.debug(f"Prompt: {prompt}")

            logger.info(
                "⏳ Waiting 1 second before GPT discrepancy check call...")
            time.sleep(1)
            response = self._call_gpt(prompt)
            # time.sleep(1)
            logger.debug(f"Discrepancy check response: {response}")

            # Parse response
            response_text = response.strip()

            # Remove markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:].strip()

            if response_text.endswith('```'):
                response_text = response_text[:-3].strip()

            response_text = response_text.strip()

            if not response_text:
                logger.error(
                    "Empty response from GPT API for discrepancy check")
                return {
                    "status": "error",
                    "error_message": "No discrepancy check result received from GPT"
                }

            result = json.loads(response_text)
            logger.info(f"✅ Discrepancy check completed")
            logger.info(f"   Items checked: {len(result.get('checks', []))}")

            return {
                "status": "success",
                "discrepancy_result": result
            }

        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing discrepancy check JSON: {str(e)}")
            logger.debug(f"Failed to parse: {response_text[:500]}")
            return {
                "status": "error",
                "error_message": f"Failed to parse discrepancy check result: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Error checking discrepancies: {str(e)}")
            logger.debug(
                f"Exception details: {type(e).__name__}", exc_info=True)
            return {
                "status": "error",
                "error_message": f"Discrepancy check failed: {str(e)}"
            }
