#!/usr/bin/env python
"""Script to test Azure configuration and connectivity"""

import sys
from pathlib import Path
import os

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all required packages are installed"""
    print("Testing Python package imports...")
    
    required_packages = [
        ("streamlit", "Streamlit"),
        ("dotenv", "python-dotenv"),
        ("requests", "requests"),
        ("PIL", "Pillow"),
    ]
    
    missing_packages = []
    
    for module, package in required_packages:
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    # Check Azure packages separately (optional in test environment)
    azure_packages = [
        ("azure.ai.documentintelligence", "azure-ai-documentintelligence"),
    ]
    
    for module, package in azure_packages:
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ⚠️  {package} (optional for testing)")
    
    return len(missing_packages) == 0, missing_packages

def test_environment():
    """Test if environment variables are properly set"""
    print("\nTesting environment variables...")
    
    required_vars = [
        "DOCUMENT_INTELLIGENCE_ENDPOINT",
        "DOCUMENT_INTELLIGENCE_KEY",
        "AZURE_AI_FOUNDRY_ENDPOINT",
        "AZURE_AI_FOUNDRY_API_KEY",
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask the actual value for security
            masked_value = f"{value[:20]}..." if len(value) > 20 else value
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ❌ {var}: NOT SET")
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def test_config():
    """Test if configuration can be loaded"""
    print("\nTesting configuration module...")
    
    try:
        from config import DOCUMENT_TYPES, validate_config
        print(f"  ✅ Configuration loaded")
        print(f"  ✅ Supported document types: {len(DOCUMENT_TYPES)}")
        
        for doc_type, info in DOCUMENT_TYPES.items():
            print(f"     - {info['ja_name']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration error: {str(e)}")
        return False

def test_document_analyzer():
    """Test Document Intelligence connectivity"""
    print("\nTesting Document Intelligence...")
    
    try:
        from document_analyzer import DocumentAnalyzer
        analyzer = DocumentAnalyzer()
        print(f"  ✅ DocumentAnalyzer initialized")
        return True
    except Exception as e:
        print(f"  ⚠️  DocumentAnalyzer initialization failed: {str(e)}")
        print(f"     (This is expected if Azure SDK is not installed or credentials are invalid)")
        return False

def test_gpt_analyzer():
    """Test GPT Analyzer initialization"""
    print("\nTesting GPT Analyzer...")
    
    try:
        from gpt_analyzer import GPTAnalyzer
        analyzer = GPTAnalyzer()
        print(f"  ✅ GPTAnalyzer initialized")
        return True
    except Exception as e:
        print(f"  ⚠️  GPTAnalyzer initialization failed: {str(e)}")
        print(f"     (This is expected if credentials are invalid)")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Trade Document Analysis - Configuration Test")
    print("=" * 60)
    
    # Test imports
    imports_ok, missing_packages = test_imports()
    
    if not imports_ok:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    # Test environment variables
    env_ok, missing_vars = test_environment()
    
    if not env_ok:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Update .env file with your Azure credentials")
        # Continue anyway - not all tests require credentials
    
    # Test configuration
    config_ok = test_config()
    
    # Test analyzers (these may fail without proper credentials)
    analyzer_ok = test_document_analyzer()
    gpt_ok = test_gpt_analyzer()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    if imports_ok and config_ok:
        print("✅ Basic setup is complete!")
        print("\nYou can now run the application:")
        print("  streamlit run src/app.py")
        
        if not env_ok:
            print("\nNote: Update .env file with Azure credentials first")
        
        return True
    else:
        print("❌ Setup is incomplete. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
