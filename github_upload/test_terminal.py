#!/usr/bin/env python3
"""
Test script for DARKNET CRYPTO MARKETPLACE Terminal Version
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError:
        print("❌ requests import failed")
        return False
    
    try:
        import cryptography
        print("✅ cryptography imported successfully")
    except ImportError:
        print("❌ cryptography import failed")
        return False
    
    try:
        import web3
        print("✅ web3 imported successfully")
    except ImportError:
        print("❌ web3 import failed")
        return False
    
    return True

def test_files():
    """Test if required files exist"""
    print("\nTesting required files...")
    
    required_files = [
        "terminal_main.py",
        "crypto_rooms.py",
        "live_market_data.py",
        "wallet_manager.py",
        "ethereum_wallet.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def test_network():
    """Test network connectivity"""
    print("\nTesting network connectivity...")
    
    try:
        import requests
        response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=5)
        if response.status_code == 200:
            print("✅ Network connectivity OK")
            return True
        else:
            print("⚠️  Network connectivity issues")
            return False
    except Exception as e:
        print(f"⚠️  Network connectivity issues: {e}")
        return False

def main():
    """Main test function"""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    DARKNET CRYPTO MARKETPLACE v2.1                           ║")
    print("║                              TERMINAL TEST                                   ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please install dependencies:")
        print("   pip install -r requirements_terminal.txt")
        return False
    
    # Test files
    if not test_files():
        print("\n❌ File test failed. Please ensure all files are present.")
        return False
    
    # Test network
    test_network()
    
    print("\n✅ All tests completed!")
    print("\nTo run the application:")
    print("   python terminal_main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 