"""Configuration module for Trade Document Analysis App"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure Document Intelligence Configuration
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv(
    "DOCUMENT_INTELLIGENCE_ENDPOINT",
    "https://<your-resource-name>.cognitiveservices.azure.com/"
)
DOCUMENT_INTELLIGENCE_KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY", "")

# Azure AI Foundry Configuration
AZURE_AI_FOUNDRY_ENDPOINT = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT", "")
AZURE_AI_FOUNDRY_API_KEY = os.getenv("AZURE_AI_FOUNDRY_API_KEY", "")
AZURE_AI_FOUNDRY_MODEL = os.getenv("AZURE_AI_FOUNDRY_MODEL", "gpt-4-mini")

# Document Types Configuration
DOCUMENT_TYPES = {
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
        "extract_fields": [
            "L/C番号", "開設依頼人", "受益者", "L/C期限", "船積期限",
            "呈示期間", "L/C開設金額", "現在残", "商品", "原産地",
            "船積地(国名)", "荷揚地(国名)", "要求書類(通数)"
        ]
    }
}

# Validate configuration


def validate_config():
    """Validate that all required environment variables are set"""
    missing_vars = []

    if not DOCUMENT_INTELLIGENCE_KEY:
        missing_vars.append("DOCUMENT_INTELLIGENCE_KEY")
    if not AZURE_AI_FOUNDRY_API_KEY:
        missing_vars.append("AZURE_AI_FOUNDRY_API_KEY")

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}")


if __name__ == "__main__":
    validate_config()
    print("Configuration validated successfully!")
