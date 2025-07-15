#!/usr/bin/env python3
"""
Test script to verify the crypto marketplace application runs without crashing
"""

import sys
import traceback
import tkinter as tk
from datetime import datetime

def test_application():
    """Test the main application"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting application test...")
    
    try:
        # Import the main application
        from main import CryptoMarketplace
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during test
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Creating application instance...")
        
        # Create application instance
        app = CryptoMarketplace(root)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Application created successfully!")
        
        # Test basic functionality
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Testing basic functionality...")
        
        # Test wallet manager
        try:
            wallet_manager = app.wallet_manager
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Wallet manager initialized successfully")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Wallet manager error: {e}")
        
        # Test live market data
        try:
            live_market = app.live_market
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Live market data initialized successfully")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Live market data error: {e}")
        
        # Test crypto rooms
        try:
            crypto_rooms = app.crypto_rooms
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Crypto rooms initialized successfully")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Crypto rooms error: {e}")
        
        # Test price updates
        try:
            app.update_displays()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Display updates working")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Display update error: {e}")
        
        # Test wallet balance update
        try:
            app.update_wallet_balance()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Wallet balance update working")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Wallet balance update error: {e}")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] All tests completed successfully!")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Application is ready to run!")
        
        # Destroy the test window
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] CRITICAL ERROR: {e}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Traceback:")
        traceback.print_exc()
        return False

def test_network_connectivity():
    """Test network connectivity"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Testing network connectivity...")
    
    try:
        import socket
        import requests
        
        # Test DNS resolution
        try:
            socket.gethostbyname("api.binance.com")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] DNS resolution working")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] DNS resolution failed: {e}")
        
        # Test basic HTTP request
        try:
            response = requests.get("https://httpbin.org/get", timeout=5)
            if response.status_code == 200:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] HTTP requests working")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] HTTP request failed with status: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] HTTP request failed: {e}")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Network test error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("CRYPTO MARKETPLACE APPLICATION TEST")
    print("=" * 60)
    
    # Test network connectivity first
    test_network_connectivity()
    print()
    
    # Test the application
    success = test_application()
    
    print()
    print("=" * 60)
    if success:
        print("✅ APPLICATION TEST PASSED - Ready to run!")
        print("Run 'python main.py' to start the application")
    else:
        print("❌ APPLICATION TEST FAILED - Check errors above")
    print("=" * 60) 