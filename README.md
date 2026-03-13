# Trade Document Analysis Demo App

## Overview

このアプリは、Pythonで構築された貿易書類分析システムです。ユーザーがアップロードしたPDFファイル（Invoice、Bill of Ladingなど）をAzure Document IntelligenceとAzure AI Foundry (GPT-4-mini)を使用して分析し、書類の種類を判別して詳細情報を抽出します。

## Architecture

### Components

- **Frontend**: Streamlit
- **Document Analysis**: Azure Document Intelligence (Layout Model)
- **AI Analysis**: Azure AI Foundry (GPT-4-mini)
- **Configuration**: Environment variables (.env)

### Supported Document Types

1. インボイス（Commercial Invoice）
2. 船荷証券（Bill of Lading - B/L）
3. 航空運送状（Air Waybill - AWB）
4. 保険証券（Insurance Policy）
5. 為替手形（Bill of Exchange）
6. 信用状（Letter of Credit - L/C）

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Azure subscription with:
  - Document Intelligence resource
  - Azure AI Foundry project with GPT-4-mini model

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
   # - AZURE_AI_FOUNDRY_ENDPOINT
   # - AZURE_AI_FOUNDRY_API_KEY
   # - AZURE_AI_FOUNDRY_MODEL (default: gpt-4-mini)
   ```

### Getting Azure Credentials

#### Document Intelligence

1. Go to [Azure Portal](https://portal.azure.com)
2. Create or select a "Document Intelligence" resource
3. Copy the endpoint URL and API key from the "Keys and Endpoint" section

#### Azure AI Foundry

1. Go to [Azure AI Foundry](https://ai.azure.com)
2. Create a project or select existing one
3. Deploy a GPT-4-mini model
4. Get the API endpoint and key from the deployment settings

## Running the Application

### Start Streamlit App

```bash
streamlit run src/app.py
```

The app will open in your default browser at `http://localhost:8501`

## Features

### Frontend (Streamlit)

- **File Upload**: Upload PDF documents at the top of the interface
- **Analysis Button**: Process the document with a single click
- **Clear Button**: Reset uploaded files and results
- **Scrollable Results**: Display document type and extracted information
- **Supported Document Types**: Expandable section showing all supported document types

### Backend

- **Two-step Analysis**:
  1. Document Classification: Identify document type
  2. Detailed Extraction: Extract specific fields based on document type
- **Azure Document Intelligence**: Uses Layout model to extract text and table structures
- **Azure AI Foundry**: Uses GPT-4-mini for intelligent classification and extraction

## Data Extraction Fields

### インボイス (Commercial Invoice)

- 商品名、輸出者名、輸入者名、FOB、CFR

### 船荷証券 (Bill of Lading)

- 商品名、輸出者名、輸入者名、船積日、呈示期限、SHIPPER、CONSIGNEE、NOTIFY、裏書

### 航空運送状 (Air Waybill)

- 商品名、輸出者名、輸入者名、船積日

### 保険証券 (Insurance Policy)

- 保険種類、被保険者、保険金額、有効期限

### 為替手形 (Bill of Exchange)

- 輸出者名、輸入者名、手形金額、満期日

### 信用状 (Letter of Credit)

- L/C番号、開設依頼人、受益者、L/C期限、船積期限、呈示期間、L/C開設金額、現在残、商品、原産地、船積地、荷揚地、要求書類

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

- Missing or invalid Azure credentials
- Document extraction failures
- GPT API errors
- Unsupported document formats

## Performance Considerations

- Document processing time depends on file size and complexity
- GPT analysis may take 10-30 seconds depending on document length
- Recommend keeping extracted text under 3000 characters for optimal GPT performance

## Troubleshooting

### Import Error for azure.ai.documentintelligence

```bash
# Make sure the correct package is installed
pip install azure-ai-documentintelligence --upgrade
```

### Connection Issues

- Verify Azure credentials in .env file
- Check that endpoints are correct (including trailing slashes)
- Ensure your Azure resources are in the same region for optimal performance

### GPT API Errors

- Check that the model name matches your deployment
- Verify API key has necessary permissions
- Check rate limiting and quota usage in Azure portal

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review Azure documentation for Document Intelligence and AI Foundry
3. Check application logs in the Streamlit interface

## Next Steps

- Add support for more document types
- Implement batch processing for multiple documents
- Add document template matching
- Enhance GPT prompts with few-shot examples
- Add export functionality for results (CSV, Excel)
