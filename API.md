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
        "extract_fields": ["商品名", "輸出者名", "輸入者名", "FOB", "CFR"]
    },
    # ... other document types
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

| 変数名 | 説明 | 必須 |
|-------|------|------|
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | Document Intelligence のエンドポイントURL | ✅ |
| `DOCUMENT_INTELLIGENCE_KEY` | Document Intelligence のAPIキー | ✅ |
| `AZURE_AI_FOUNDRY_ENDPOINT` | Azure AI Foundry のエンドポイントURL | ✅ |
| `AZURE_AI_FOUNDRY_API_KEY` | Azure AI Foundry のAPIキー | ✅ |
| `AZURE_AI_FOUNDRY_MODEL` | 使用するGPTモデル (デフォルト: gpt-4-mini) | ❌ |

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

Azure AI Foundry の GPT モデルを使用して、ドキュメント分類と詳細情報抽出を行います。

#### Constructor

```python
from gpt_analyzer import GPTAnalyzer

analyzer = GPTAnalyzer()
```

#### Method: `analyze_document(extracted_text, tables_data)`

2段階の分析を実行します：
1. ドキュメント種類の分類
2. 分類に基づいた詳細情報の抽出

**Parameters:**
- `extracted_text` (str): Document Intelligence から抽出されたテキスト
- `tables_data` (list): Document Intelligence から抽出されたテーブルデータ

**Returns:**
```python
{
    "status": "success" | "error",
    "document_type": {
        "ja_name": str,  # "インボイス（商業送り状）"
        "en_name": str   # "Commercial Invoice"
    },
    "document_class": str,  # "invoice", "bill_of_lading", etc.
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
st.session_state.uploaded_file      # アップロードされたファイル
st.session_state.analysis_result    # 分析結果
st.session_state.document_analyzer  # DocumentAnalyzer インスタンス
st.session_state.gpt_analyzer       # GPTAnalyzer インスタンス
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

### Example 1: Simple Document Analysis

```python
from document_analyzer import DocumentAnalyzer
from gpt_analyzer import GPTAnalyzer

# Initialize analyzers
doc_analyzer = DocumentAnalyzer()
gpt_analyzer = GPTAnalyzer()

# Read document
with open("commercial_invoice.pdf", "rb") as f:
    file_bytes = f.read()

# Analyze with Document Intelligence
doc_result = doc_analyzer.analyze_document(file_bytes, "invoice.pdf")

if doc_result["status"] == "success":
    # Analyze with GPT
    gpt_result = gpt_analyzer.analyze_document(
        doc_result["extracted_text"],
        doc_result["tables"]
    )
    
    # Print results
    if gpt_result["status"] == "success":
        doc_type = gpt_result["document_type"]["ja_name"]
        fields = gpt_result["detailed_information"]["fields"]
        
        print(f"Document Type: {doc_type}")
        for field, value in fields.items():
            print(f"  {field}: {value}")
```

### Example 2: Batch Processing

```python
from pathlib import Path
from document_analyzer import DocumentAnalyzer
from gpt_analyzer import GPTAnalyzer
import json

doc_analyzer = DocumentAnalyzer()
gpt_analyzer = GPTAnalyzer()

# Process all PDFs in a directory
pdf_dir = Path("./documents")
results = []

for pdf_file in pdf_dir.glob("*.pdf"):
    print(f"Processing {pdf_file.name}...")
    
    with open(pdf_file, "rb") as f:
        doc_result = doc_analyzer.analyze_document(f.read(), pdf_file.name)
    
    if doc_result["status"] == "success":
        gpt_result = gpt_analyzer.analyze_document(
            doc_result["extracted_text"],
            doc_result["tables"]
        )
        
        results.append({
            "file": pdf_file.name,
            "result": gpt_result
        })

# Save results
with open("analysis_results.json", "w", encoding="utf-8") as f:
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

### Text Length Limits

- Document Intelligence: 無制限
- GPT API: 4096 トークン以下 (約3000-4000文字)

### Optimization Tips

1. **大きなドキュメントの場合:**
   - 特定のページのみを抽出
   - テキストを事前処理して短縮

2. **複数ドキュメント処理:**
   - 非同期処理を使用
   - バッチ処理でAPI呼び出しを最適化

3. **費用削減:**
   - 不要なテーブル抽出を無効化
   - キャッシング機構を実装

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
