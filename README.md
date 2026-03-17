# Trade Document Analysis Demo App

## Overview

このアプリは、**Letter of Credit (L/C) を基準ドキュメント**として、関連する複数の貿易書類（Invoice、Bill of Lading など）のディスクレパンシーを自動チェックするシステムです。Azure Document Intelligence による OCR と Azure OpenAI (GPT-5-mini) による AI 分析で、10 項目の詳細な検証を実施し、信用状に対する書類の相違を自動検出します。

## Architecture

### Components

- **Frontend**: Streamlit
- **Document Analysis**: Azure Document Intelligence (Layout Model)
- **AI Analysis**: Azure OpenAI (GPT-5-mini model)
- **Configuration**: Environment variables (.env)

### Workflow

```
┌─ L/C ファイルアップロード (左側)
│  ├─ OCR 抽出
│  ├─ 文書種別判定 (GPT: L/C 確認)
│  └─ フィールド抽出
│
├─ 関連書類マルチアップロード (右側)
│  ├─ ファイル1 (Invoice, B/L, AWB など): 順次分析
│  ├─ ファイル2: 分析
│  └─ ...複数ファイル対応
│
└─ 10項目ディスクレチェック実行
   ├─ 船積日、L/C有効期限、呈示期限チェック
   ├─ 要求書類、建値、港湾、商品チェック
   ├─ 決済方法、手数料、ユーザンス期日チェック
   └─ 結果表示（色分け: ✅ OK / ❌ NG / ⚠️ Warning）
```

### Supported Document Types

**基準ドキュメント:**

- 信用状（Letter of Credit - L/C）**← アップロード必須 (左側)**

**比較対象ドキュメント (複数同時アップロード可):**

1. インボイス（Commercial Invoice）
2. 船荷証券（Bill of Lading - B/L）
3. 航空運送状（Air Waybill - AWB）
4. 保険証券（Insurance Policy）
5. 為替手形（Bill of Exchange）
6. その他の補足書類

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Azure subscription with:
  - Document Intelligence resource
  - Azure OpenAI Service (GPT-5-mini model deployed)

### Installation

1. **Navigate to project**

   ```bash
   cd trade-doc-analysis
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**

   ```bash
   # Copy the example file
   copy .env.example .env

   # Edit .env with your Azure credentials
   # Required variables:
   # - DOCUMENT_INTELLIGENCE_ENDPOINT
   # - DOCUMENT_INTELLIGENCE_KEY
   # - AZURE_OPENAI_ENDPOINT
   # - AZURE_OPENAI_API_KEY
   # - AZURE_OPENAI_MODEL_NAME (default: gpt-5-mini)
   ```

### Getting Azure Credentials

#### Document Intelligence

1. Go to [Azure Portal](https://portal.azure.com)
2. Create or select a "Document Intelligence" resource
3. Copy the endpoint URL and API key from the "Keys and Endpoint" section

#### Azure OpenAI

1. Go to [Azure Portal](https://portal.azure.com)
2. Create or select an "Azure OpenAI" resource
3. Deploy a "gpt-5-mini" model
4. Copy the endpoint URL and API key from the resource's "Keys and Endpoint" section

## Running the Application

### Start Streamlit App

```bash
streamlit run src/app.py
```

The app will open in your default browser at `http://localhost:8501`

## Features

### L/C Discrepancy Checking System

- **Single L/C Reference**: Upload Letter of Credit as the reference document (left side, mandatory)
- **Multiple Document Analysis**: Upload multiple related documents (Invoice, B/L, AWB, etc.) simultaneously (right side)
- **10-Item Automated Checks**:
  1. 船積日（Shipment Date）- B/L との比較
  2. L/C 有効期限（L/C Expiration）
  3. 呈示期限（Presentation Period）- B/L との比較
  4. 要求書類の不備（Required Documents Count）
  5. 建値（Price Terms: FOB/CFR vs FREIGHT PREPAID/COLLECT）
  6. 港湾（Ports: Shipment & Discharge Ports）
  7. 商品（Goods Description）- B/L と Invoice との比較
  8. 対外決済方法（Settlement Method & SWIFT Address）
  9. 手数料・条件（Fees & Conditions: P/O, S/A, A/A）
  10. ユーザンス期日（Usance Period）

### Frontend (Streamlit)

- **Split Upload Interface**: L/C (左) と複数書類 (右) を分離して入力
- **Dual-Column Display**: L/C 情報 + 複数ファイルをタブ表示
- **Color-Coded Results**:
  - **✅ OK** (緑): 相違なし
  - **❌ NG** (赤): 相違あり
  - **⚠️ Warning** (黄): 注意が必要
- **Critical Issues Summary**: 重大な問題を強調表示
- **Recommendations**: 修正すべき項目の推奨事項を提示

### Backend

- **3-Step Processing**:
  1. L/C 分析・検証: ファイルが Letter of Credit か確認（不可の場合、処理中断）
  2. 複数ファイル順次分析: 各ファイルを種別判定・抽出
  3. ディスクレチェック実行: GPT により 10 項目を詳細分析
- **Azure Document Intelligence**: Layout model による OCR
- **Azure OpenAI**: GPT-5-mini による文書分類・抽出・比較分析
- **API Rate Limiting**: 各 GPT 呼び出し前に 1 秒遅延を実装（計4回）

## Data Extraction Fields

### Letter of Credit (L/C) - Required Reference Document

- L/C番号、開設依頼人、受益者
- L/C期限、船積期限、呈示期間
- L/C開設金額、現在残
- 商品、原産地、船積地、荷揚地
- 要求書類（通数）、特別条件

### Commercial Invoice

- 輸出者名、輸入者名、商品名
- FOB、CFR、金額
- 発行日、請求先

### Bill of Lading (B/L)

- 輸出者名、荷受人名、貨物到着通知先
- 船積港、仕向港、商品名
- 船積日、ON BOARD表示、呈示期限
- 通数、B/L発行日、B/L発行者

### Air Waybill (AWB)

- 輸出者名、荷受人名、貨物到着通知先
- 船積港、仕向港、商品名
- 船積日、AWB発行日

### Other Documents

- 保険証券 (Insurance Policy): 保険証券番号、保険種類、被保険者、保険金額、商品名
- 為替手形 (Bill of Exchange): 支払人、振出人、手形金額、満期日

## Project Structure

```
trade-doc-analysis/
├── src/
│   ├── app.py                 # Streamlit main application
│   ├── config.py              # Configuration and environment variables
│   ├── document_analyzer.py    # Azure Document Intelligence wrapper
│   └── gpt_analyzer.py         # Azure AI Foundry GPT analysis
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Local environment variables (not in git)
├── README.md                 # This file
└── LICENSE                   # License file
```

## Error Handling

The application includes error handling for:

- **Missing Azure credentials**: Invalid or missing .env variables
- **Document extraction failures**: OCR processing errors
- **GPT API errors**: API rate limiting, timeout, or service errors
- **L/C Validation Error**: Non-L/C file uploaded → processing stops immediately
- **Unsupported document formats**: Non-PDF or incompatible files
- **Empty response errors**: GPT returns empty or malformed JSON
- **Semantic resolution**: Automatic retry with improved prompts on JSON parsing errors

## Performance Considerations

- **OCR Processing**: Document Intelligence processing time varies by file size (5-15 seconds per document)
- **GPT Analysis**: L/C classification, extraction, and discrepancy checking use 4 sequential GPT calls
- **API Rate Limiting**: 1-second mandatory delay before each of 4 GPT API calls (≈4 seconds additional)
- **Total Processing Time**: Typically 30-60 seconds for L/C + 2-3 related documents
- **Recommended Document Complexity**: Optimal performance with extracted text under 4000 characters per document
- **Multi-File Impact**: Each additional document adds ~5 seconds for OCR + GPT extraction

## Troubleshooting

### Import Error for azure.ai.documentintelligence

```bash
# Make sure the correct package is installed
pip install azure-ai-documentintelligence --upgrade
```

### L/C Validation Error

If you see "Uploaded file is not a Letter of Credit":

- Verify you uploaded a valid Letter of Credit PDF
- Check that the L/C contains expected fields (L/C number, expiration date, etc.)
- Ensure the L/C metadata is clearly labeled in the document

### Connection Issues

- Verify Azure credentials in .env file
- Check that endpoints are correct (including trailing slashes)
- Ensure your Azure resources are in the same region for optimal performance
- Verify Document Intelligence API key has read permissions

### Azure OpenAI Errors

- Check that the model name matches your deployment ("gpt-5-mini")
- Verify API key has necessary permissions
- Check rate limiting and quota usage in Azure portal
- Confirm AZURE_OPENAI_ENDPOINT is correctly formatted: `https://{resource}.openai.azure.com/`

### Multi-File Upload Issues

- Ensure at least one file (other than L/C) is uploaded for discrepancy checking
- Files should be in PDF format
- Total file size should not exceed resource limits

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review Azure documentation for Document Intelligence and AI Foundry
3. Check application logs in the Streamlit interface

## Next Steps & Roadmap

- **Enhanced L/C Validation**: Add support for different L/C types (Irrevocable, Revolving, Standby)
- **Advanced Discrepancy Analysis**: Implement machine learning for semantic similarity scoring
- **Batch Processing**: Support processing of multiple L/C documents in a single session
- **Export Functionality**: Generate PDF/Excel reports with detailed discrepancy findings
- **Audit Trail**: Log all checks and findings for compliance documentation
- **Custom Rule Engine**: Allow users to define custom discrepancy checking rules
- **Multi-Language Support**: Support for documents in multiple languages
- **Integration with Trade Finance Systems**: Export findings to ERP/TMS systems
