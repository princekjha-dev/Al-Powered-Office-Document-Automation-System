#!/usr/bin/env python3
"""
Quick setup and test script for the Al-Powered Office Document Automation System.
"""

import os
import sys
import subprocess

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import telegram
        import PyPDF2
        import docx
        import openpyxl
        import dotenv
        import reportlab
        import PIL
        import fastapi
        import uvicorn
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required keys."""
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        return False

    from dotenv import load_dotenv
    load_dotenv()

    required_keys = ['TELEGRAM_TOKEN', 'OPENROUTER_API_KEY']
    missing_keys = []

    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)

    if missing_keys:
        print(f"❌ Missing environment variables: {', '.join(missing_keys)}")
        return False

    print("✅ Environment variables configured")
    return True

def check_directories():
    """Check if required directories exist."""
    dirs = ['data/users', 'data/galleries', 'data/sessions']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
            print(f"✅ Created directory: {d}")
        else:
            print(f"✅ Directory exists: {d}")
    return True

def test_imports():
    """Test if all modules can be imported."""
    try:
        # Test main imports
        from src.config.settings import Config
        from src.utils.helpers import setup_logging
        from src.models.user import UserManager
        from src.models.storage import UserGalleryStorage
        from src.services.document_reader import DocumentReader
        from src.services.ai_generation import AIGenerationService

        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    try:
        from src.config.settings import Config
        Config.validate()
        Config.create_directories()
        print("✅ Configuration validated")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all checks."""
    print("🚀 Al-Powered Office Document Automation System - Setup Check")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Directories", check_directories),
        ("Imports", test_imports),
        ("Configuration", test_config),
    ]

    passed = 0
    total = len(checks)

    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        if check_func():
            passed += 1

    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All checks passed! Your bot is ready to run.")
        print("\n🚀 To start the bot:")
        print("   python bot.py")
        print("\n📚 For help:")
        print("   /start - Start the bot")
        print("   /help - Show all commands")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("   • Install dependencies: pip install -r requirements.txt")
        print("   • Create .env file with your API keys")
        print("   • Check Python version: python --version")

    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)