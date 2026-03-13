"""Quick start script for Trade Document Analysis App"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  .env file not found")
        print("📋 Creating .env from .env.example...")
        
        example_path = Path(".env.example")
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)
            print("✅ .env file created")
            print("⚠️  Please update .env with your Azure credentials")
        else:
            print("❌ .env.example file not found")
            sys.exit(1)
    else:
        print("✅ .env file found")

def check_venv():
    """Check if virtual environment is active"""
    if sys.prefix == sys.base_prefix:
        print("⚠️  Virtual environment not activated")
        print("📋 To activate, run:")
        print("   Windows: venv\\Scripts\\activate")
        print("   Mac/Linux: source venv/bin/activate")
    else:
        print(f"✅ Virtual environment active: {sys.prefix}")

def main():
    """Run startup checks"""
    print("=" * 50)
    print("Trade Document Analysis - Startup Check")
    print("=" * 50)
    print()
    
    check_python_version()
    print()
    
    check_venv()
    print()
    
    check_env_file()
    print()
    
    print("=" * 50)
    print("To start the application, run:")
    print("  streamlit run src/app.py")
    print("=" * 50)

if __name__ == "__main__":
    main()
