# API Documentation for Trade Document Analysis

## Overview

このドキュメントでは、貿易書類分析アプリの内部APIと使用方法について説明します。

## Configuration Module (`config.py`)

### Constants

#### `DOCUMENT_TYPES`

書類種類の定義と抽出対象フィールドを含む辞書。

```python
{
    "invoice": {
        "ja_name": "インボイス（商業送り状）",
        "en_name": "Commercial Invoice",
        "extract_fields": ["輸出者名", "輸入者名", "商品名", "FOB", "CFR", "金額"]
    },
    "bill_of_lading": {
        "ja_name": "船荷証券",
        "en_name": "Bill of Lading (B/L)",
        "extract_fields": ["輸出者名", "荷受人名", "貨物到着通知先", "船積港", "仕向港", "商品名", "船積日", "ON BOARD表示", "呈示期限", "通数", "B/L発行日", "B/L発行者"]
    },
    "air_waybill": {
        "ja_name": "航空運送状",
        "en_name": "Air Waybill (AWB)",
        "extract_fields": ["輸出者名", "荷受人名", "貨物到着通知先", "船積港", "仕向港", "商品名", "船積日", "ON BOARD表示", "呈示期限", "通数", "B/L発行日", "B/L発行者"]
    },
    "insurance_policy": {
        "ja_name": "保険証券",
        "en_name": "Insurance Policy",
        "extract_fields": ["保険証券番号", "保険種類", "被保険者", "保険金額", "損害填補範囲", "商品名", "有効期限", "保険会社名"]
    },
    "bill_of_exchange": {
        "ja_name": "為替手形",
        "en_name": "Bill of Exchange",
        "extract_fields": ["支払人", "振出人", "手形金額", "満期日"]
    },
    "letter_of_credit": {
        "ja_name": "信用状",
        "en_name": "Letter of Credit (L/C)",
        "extract_fields": ["L/C番号", "開設依頼人", "受益者", "L/C期限", "船積期限", "呈示期間", "L/C開設金額", "現在残", "商品", "原産地", "船積地(国名)", "荷揚地(国名)", "要求書類(通数)"]
    }
}
```

### Functions

#### `validate_config()`

環境変数の検証を行う。必須の環境変数がすべて設定されていることを確認します。

```python
from config import validate_config

try:
    validate_config()
    print("Configuration is valid")
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Environment Variables

| 変数名                           | 説明                                       | 必須 |
| -------------------------------- | ------------------------------------------ | ---- |
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | Document Intelligence のエンドポイントURL  | ✅   |
| `DOCUMENT_INTELLIGENCE_KEY`      | Document Intelligence のAPIキー            | ✅   |
| `AZURE_OPENAI_ENDPOINT`          | Azure OpenAI Service のエンドポイントURL   | ✅   |
| `AZURE_OPENAI_API_KEY`           | Azure OpenAI Service のAPIキー             | ✅   |
| `AZURE_OPENAI_MODEL_NAME`        | 使用するGPTモデル (デフォルト: gpt-5-mini) | ❌   |

## Document Analyzer Module (`document_analyzer.py`)

### Class: `DocumentAnalyzer`

Azure Document Intelligence を使用したドキュメント分析を行います。

#### Constructor

```python
from document_analyzer import DocumentAnalyzer

analyzer = DocumentAnalyzer()
```

#### Method: `analyze_document(file_bytes, file_name)`

ドキュメントを分析し、テキストとテーブルデータを抽出します。

**Parameters:**

- `file_bytes` (bytes): PDFファイルのバイナリコンテンツ
- `file_name` (str): ファイル名

**Returns:**

```python
{
    "status": "success" | "error",
    "file_name": str,
    "extracted_text": str,        # 抽出されたテキスト
    "tables": [                    # テーブル構造
        {
            "table_index": int,
            "content": [
                {
                    "row": int,
                    "column": int,
                    "content": str
                }
            ]
        }
    ],
    "page_count": int,
    "error_message": str           # status="error" の場合のみ
}
```

**Example:**

```python
analyzer = DocumentAnalyzer()

with open("invoice.pdf", "rb") as f:
    result = analyzer.analyze_document(f.read(), "invoice.pdf")

if result["status"] == "success":
    print(f"Extracted text: {result['extracted_text'][:100]}...")
    print(f"Number of tables: {len(result['tables'])}")
else:
    print(f"Error: {result['error_message']}")
```

## GPT Analyzer Module (`gpt_analyzer.py`)

### Class: `GPTAnalyzer`

Azure OpenAI Service の GPT-5-mini モデルを使用して、ドキュメント分類、詳細情報抽出、および Letter of Credit ベースのディスクレパンシーチェックを行います。

#### Constructor

```python
from gpt_analyzer import GPTAnalyzer

analyzer = GPTAnalyzer()
```

#### Method: `analyze_document(extracted_text, tables_data, is_lc=False)`

2段階の分析を実行します：

1. ドキュメント種類の分類
2. 分類に基づいた詳細情報の抽出

**Parameters:**

- `extracted_text` (str): Document Intelligence から抽出されたテキスト
- `tables_data` (list): Document Intelligence から抽出されたテーブルデータ
- `is_lc` (bool): True の場合、L/C であることを確認，False の場合，通常の分類・抽出を実施

**Returns:**

```python
{
    "status": "success" | "error",
    "document_type": {
        "ja_name": str,  # "インボイス（商業送り状）"
        "en_name": str   # "Commercial Invoice"
    },
    "document_class": str,  # "invoice", "bill_of_lading", "letter_of_credit", etc.
    "detailed_information": {
        "fields": {
            "field_name": "extracted_value",
            ...
        },
        "additional_notes": str
    },
    "error_message": str  # status="error" の場合のみ
}
```

#### Method: `check_discrepancies_with_lc(lc_analysis, other_files_analyses)`

Letter of Credit を基準に、関連書類のディスクレパンシーを 10 項目にわたって詳細チェックします。

**Parameters:**

- `lc_analysis` (dict): L/C の分析結果（`analyze_document()` の返り値）
- `other_files_analyses` (dict): その他の書類の分析結果の辞書 `{document_type: analysis_result}`

  例:

  ```python
  {
      "invoice": {analysis_result},
      "bill_of_lading": {analysis_result},
      ...
  }
  ```

**Returns:**

```python
{
    "status": "success" | "error",
    "checks": {
        "shipment_date_verification": {
            "status": "OK" | "NG" | "Warning",
            "detail": "詳細な検証結果",
            "bl_shipment_date": "2024-03-15",
            "lc_shipment_deadline": "2024-03-31"
        },
        "lc_expiration_check": {...},
        "presentation_period_check": {...},
        "required_documents_check": {...},
        "price_terms_check": {...},
        "ports_verification": {...},
        "goods_description_check": {...},
        "settlement_method_check": {...},
        "fees_and_conditions_check": {...},
        "usance_period_check": {...}
    },
    "summary": {
        "total_items": 10,
        "ok_count": int,
        "ng_count": int,
        "warning_count": int,
        "overall_status": "OK" | "NG" | "Warning"
    },
    "critical_issues": [
        "重大な問題1",
        "重大な問題2"
    ],
    "warnings": [
        "警告1",
        "警告2"
    ],
    "recommendations": [
        "推奨事項1",
        "推奨事項2"
    ],
    "error_message": str  # status="error" の場合のみ
}
```

**Example:**

```python
from document_analyzer import DocumentAnalyzer
from gpt_analyzer import GPTAnalyzer

doc_analyzer = DocumentAnalyzer()
gpt_analyzer = GPTAnalyzer()

# Step 1: Extract document content
with open("invoice.pdf", "rb") as f:
    doc_result = doc_analyzer.analyze_document(f.read(), "invoice.pdf")

if doc_result["status"] == "success":
    # Step 2: Analyze with GPT
    gpt_result = gpt_analyzer.analyze_document(
        doc_result["extracted_text"],
        doc_result["tables"]
    )

    if gpt_result["status"] == "success":
        print(f"Document Type: {gpt_result['document_type']['ja_name']}")
        print(f"Extracted Fields: {gpt_result['detailed_information']['fields']}")
```

## Streamlit Application (`app.py`)

### Session State

アプリはStreamlit session stateで以下の値を管理します：

```python
# L/C (基準ドキュメント)
st.session_state.uploaded_lc              # アップロードされた Letter of Credit ファイル
st.session_state.lc_analysis_result       # L/C の分析結果

# 複数の関連書類
st.session_state.uploaded_other_files     # アップロードされた関連書類（複数）
st.session_state.other_files_analysis_results  # 各関連書類の分析結果 {doc_type: analysis_result}

# ディスクレチェック
st.session_state.discrepancy_check_result # 10 項目のディスクレチェック結果

# 分析エンジン
st.session_state.document_analyzer        # DocumentAnalyzer インスタンス
st.session_state.gpt_analyzer             # GPTAnalyzer インスタンス
```

### Main Functions

#### `initialize_analyzers()`

分析エンジンを初期化し、設定を検証します。

#### `analyze_document()`

アップロードされたドキュメントを分析します。

#### `clear_analysis()`

アップロードされたファイルと分析結果をリセットします。

#### `display_results()`

分析結果を画面に表示します。

## Usage Examples

### Example 1: L/C Discrepancy Checking

```python
from document_analyzer import DocumentAnalyzer
from gpt_analyzer import GPTAnalyzer

# Initialize analyzers
doc_analyzer = DocumentAnalyzer()
gpt_analyzer = GPTAnalyzer()

# Read L/C document
with open("letter_of_credit.pdf", "rb") as f:
    lc_file_bytes = f.read()

# Analyze L/C
doc_result = doc_analyzer.analyze_document(lc_file_bytes, "letter_of_credit.pdf")

if doc_result["status"] == "success":
    # Classify and extract L/C information
    lc_analysis = gpt_analyzer.analyze_document(
        doc_result["extracted_text"],
        doc_result["tables"],
        is_lc=True
    )

    if lc_analysis["status"] == "success" and lc_analysis["document_class"] == "letter_of_credit":
        # Process supporting documents
        other_files_analyses = {}

        for doc_path in ["invoice.pdf", "bill_of_lading.pdf"]:
            with open(doc_path, "rb") as f:
                doc_result = doc_analyzer.analyze_document(f.read(), doc_path)

            if doc_result["status"] == "success":
                analysis = gpt_analyzer.analyze_document(
                    doc_result["extracted_text"],
                    doc_result["tables"]
                )
                if analysis["status"] == "success":
                    other_files_analyses[analysis["document_class"]] = analysis

        # Run discrepancy check
        discrepancy_result = gpt_analyzer.check_discrepancies_with_lc(
            lc_analysis,
            other_files_analyses
        )

        # Display results
        print(f"L/C Number: {lc_analysis['detailed_information']['fields'].get('L/C番号')}")
        print(f"\nDiscrepancy Check Result: {discrepancy_result['summary']['overall_status']}")
        print(f"OK: {discrepancy_result['summary']['ok_count']}/10")
        print(f"NG: {discrepancy_result['summary']['ng_count']}/10")
        print(f"Warning: {discrepancy_result['summary']['warning_count']}/10")

        if discrepancy_result['critical_issues']:
            print(f"\nCritical Issues:")
            for issue in discrepancy_result['critical_issues']:
                print(f"  - {issue}")
    else:
        print("Error: Uploaded file is not a Letter of Credit")
```

### Example 2: Batch L/C Processing

```python
from pathlib import Path
from document_analyzer import DocumentAnalyzer
from gpt_analyzer import GPTAnalyzer
import json

doc_analyzer = DocumentAnalyzer()
gpt_analyzer = GPTAnalyzer()

# Process multiple L/C batches
lc_dir = Path("./lc_documents")
results = []

for lc_file in lc_dir.glob("lc_*.pdf"):
    print(f"Processing {lc_file.name}...")

    # Analyze L/C
    with open(lc_file, "rb") as f:
        result = doc_analyzer.analyze_document(f.read(), lc_file.name)

    if result["status"] == "success":
        lc_analysis = gpt_analyzer.analyze_document(
            result["extracted_text"],
            result["tables"],
            is_lc=True
        )

        # Identify and process related documents
        doc_name = lc_file.stem.replace("lc_", "")
        related_docs = list(lc_dir.glob(f"*{doc_name}*.pdf"))

        other_files_analyses = {}
        for doc_path in related_docs:
            if "lc" not in doc_path.name:
                with open(doc_path, "rb") as f:
                    doc_result = doc_analyzer.analyze_document(f.read(), doc_path.name)
                if doc_result["status"] == "success":
                    analysis = gpt_analyzer.analyze_document(
                        doc_result["extracted_text"],
                        doc_result["tables"]
                    )
                    if analysis["status"] == "success":
                        other_files_analyses[analysis["document_class"]] = analysis

        # Run discrepancy check
        if lc_analysis["status"] == "success":
            discrepancy_result = gpt_analyzer.check_discrepancies_with_lc(
                lc_analysis,
                other_files_analyses
            )

            results.append({
                "lc_file": lc_file.name,
                "lc_number": lc_analysis['detailed_information']['fields'].get('L/C番号'),
                "discrepancy_check": discrepancy_result['summary']
            })

# Save batch results
with open("lc_batch_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

## Error Handling

### Common Errors and Solutions

#### Import Error: azure.ai.documentintelligence

```
ImportError: No module named 'azure.ai.documentintelligence'
```

**Solution:**

```bash
pip install azure-ai-documentintelligence --upgrade
```

#### Configuration Error: Missing Environment Variables

```
ValueError: Missing required environment variables: DOCUMENT_INTELLIGENCE_KEY
```

**Solution:**
`.env` ファイルにすべての必須環境変数を設定してください。

#### API Error: Invalid Credentials

```
AuthenticationError: Invalid credentials
```

**Solution:**

1. Azure Portal で認証情報を確認してください
2. `.env` ファイルが正しく設定されているか確認してください
3. APIキーの有効期限を確認してください

#### API Error: Endpoint Not Found

```
RequestException: 404 Not Found
```

**Solution:**

1. エンドポイントURLが正しい形式であることを確認してください
2. リージョンが正しいことを確認してください
3. Azure リソースが作成されていることを確認してください

## Performance Optimization

### Document Size Limits

- 推奨: ファイルサイズ 10MB 以下
- 最大: 2000 ページ

### Processing Time

- **Document Intelligence (OCR)**: 5-15 秒/ドキュメント
- **GPT L/C 分類**: ~5 秒 + 1 秒遅延
- **GPT 各書類抽出**: ~5 秒 + 1 秒遅延（複数ドキュメント数分）
- **GPT ディスクレチェック**: ~10 秒 + 1 秒遅延
- **Total**: 30-60 秒（L/C + 2-3 関連書類の場合）

### Text Length Limits

- Document Intelligence: 無制限
- GPT API: 4096 トークン以下 (約3000-4000文字) per API call

### API Rate Limiting

- 各 GPT API 呼び出し前に 1 秒の遅延を実装
- 合計 4 回の遅延: L/C 分類、L/C 抽出、関連書類分析、ディスクレチェック
- 複数書類の場合、各文書ごとに平均 ~1-2 秒の追加遅延

### Optimization Tips

1. **大きなドキュメントの場合:**
   - 特定のページのみを抽出
   - テキストを事前処理して短縮

2. **複数ドキュメント処理:**
   - 3-4 つのドキュメント以上の場合は、非同期処理を検討
   - バッチ処理でAPI呼び出しを最適化

3. **費用削減:**
   - 不要なテーブル抽出を無効化
   - キャッシング機構で同一ドキュメント再分析を防止
   - トークン使用量を監視（GPT API）

4. **L/C チェック最適化:**
   - 主要 10 項目のみに絞った効率的なプロンプト использование
   - 不要な詳細抽出をスキップ

## Logging

アプリは標準的な Python logging を使用しています。

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing started")
logger.error("Processing failed")
```

ログレベルは `.env` で設定できます：

```
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## License

MIT License
