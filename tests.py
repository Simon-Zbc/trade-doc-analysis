"""Unit tests for Trade Document Analysis components"""

import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import DOCUMENT_TYPES, validate_config

class TestConfig(unittest.TestCase):
    """Test configuration module"""
    
    def test_document_types_defined(self):
        """Test that all required document types are defined"""
        required_types = [
            "invoice",
            "bill_of_lading",
            "air_waybill",
            "insurance_policy",
            "bill_of_exchange",
            "letter_of_credit"
        ]
        
        for doc_type in required_types:
            self.assertIn(doc_type, DOCUMENT_TYPES)
    
    def test_document_type_structure(self):
        """Test that document types have required fields"""
        required_fields = ["ja_name", "en_name", "extract_fields"]
        
        for doc_type, info in DOCUMENT_TYPES.items():
            for field in required_fields:
                self.assertIn(field, info)
            
            # Check that extract_fields is a list
            self.assertIsInstance(info["extract_fields"], list)
            self.assertGreater(len(info["extract_fields"]), 0)
    
    def test_extract_fields_for_invoice(self):
        """Test extract fields for invoice"""
        invoice_fields = DOCUMENT_TYPES["invoice"]["extract_fields"]
        expected_fields = ["商品名", "輸出者名", "輸入者名", "FOB", "CFR"]
        
        for field in expected_fields:
            self.assertIn(field, invoice_fields)
    
    def test_extract_fields_for_lc(self):
        """Test extract fields for Letter of Credit"""
        lc_fields = DOCUMENT_TYPES["letter_of_credit"]["extract_fields"]
        expected_fields = [
            "L/C番号", "開設依頼人", "受益者", "L/C期限", "船積期限"
        ]
        
        for field in expected_fields:
            self.assertIn(field, lc_fields)

class TestDocumentAnalyzer(unittest.TestCase):
    """Test Document Analyzer class"""
    
    def test_document_analyzer_import(self):
        """Test that DocumentAnalyzer can be imported"""
        try:
            from document_analyzer import DocumentAnalyzer
            self.assertTrue(True)
        except ImportError:
            # Azure SDK might not be installed in test environment
            self.skipTest("Azure SDK not installed")

class TestGPTAnalyzer(unittest.TestCase):
    """Test GPT Analyzer class"""
    
    def test_gpt_analyzer_import(self):
        """Test that GPTAnalyzer can be imported"""
        try:
            from gpt_analyzer import GPTAnalyzer
            self.assertTrue(True)
        except ImportError:
            self.skipTest("Dependencies not installed")

if __name__ == "__main__":
    unittest.main()
