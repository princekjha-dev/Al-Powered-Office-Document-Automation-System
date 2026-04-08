#!/usr/bin/env python3
"""
Simple test script to verify the bot setup.
Run this after setting up your .env file.
"""

import os
import sys

def test_imports():
    """Test basic imports."""
    try:
        print("🔍 Testing imports...")
        from src.config.settings import Config
        from src.utils.helpers import setup_logging
        from src.models.user import UserManager
        from src.services.ai_generation import AIGenerationService
        print("✅ Imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration."""
    try:
        print("🔍 Testing configuration...")
        from src.config.settings import Config
        Config.validate()
        print("✅ Configuration valid")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_env():
    """Test environment variables."""
    print("🔍 Testing environment...")
    required = ['TELEGRAM_TOKEN', 'OPENROUTER_API_KEY']
    missing = []

    for key in required:
        if not os.getenv(key):
            missing.append(key)

    if missing:
        print(f"❌ Missing: {', '.join(missing)}")
        return False

    print("✅ Environment variables set")
    return True

def main():
    """Run tests."""
    print("🧪 Bot Setup Test")
    print("=" * 30)

    tests = [
        ("Environment", test_env),
        ("Imports", test_imports),
        ("Configuration", test_config),
    ]

    passed = 0
    for name, test_func in tests:
        if test_func():
            passed += 1
        print()

    print("=" * 30)
    if passed == len(tests):
        print("🎉 All tests passed! Run: python bot.py")
    else:
        print("❌ Fix issues above before running bot")

    return passed == len(tests)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)