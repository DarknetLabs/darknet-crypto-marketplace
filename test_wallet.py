#!/usr/bin/env python3
"""
Test script for Ethereum wallet functionality
"""

from ethereum_wallet import EthereumWallet
import time

def test_wallet_functionality():
    """Test basic wallet operations"""
    print("=== ETHEREUM WALLET TEST ===")
    print()
    
    # Initialize wallet manager
    wallet = EthereumWallet()
    
    # Test wallet creation
    print("1. Creating test wallet...")
    address, wallet_data = wallet.generate_wallet("Test Wallet", "testpassword123")
    print(f"   Wallet created: {address}")
    print(f"   Wallet name: {wallet_data['name']}")
    print()
    
    # Test wallet unlocking
    print("2. Unlocking wallet...")
    success, message = wallet.unlock_wallet(address, "testpassword123")
    print(f"   Unlock result: {message}")
    print()
    
    # Test balance checking
    print("3. Checking wallet balance...")
    balance = wallet.get_wallet_balance()
    print(f"   Balance: {balance} ETH")
    print()
    
    # Test wallet info
    print("4. Getting wallet info...")
    info = wallet.get_wallet_info(address)
    if info:
        print(f"   Name: {info['name']}")
        print(f"   Address: {info['address']}")
        print(f"   Created: {info['created_at']}")
    print()
    
    # Test transaction history
    print("5. Getting transaction history...")
    transactions = wallet.get_transaction_history()
    print(f"   Found {len(transactions)} transactions")
    print()
    
    # Test wallet locking
    print("6. Locking wallet...")
    wallet.lock_wallet()
    print("   Wallet locked")
    print()
    
    # Test wallet list
    print("7. Listing all wallets...")
    wallets = wallet.list_wallets()
    print(f"   Found {len(wallets)} wallets:")
    for addr in wallets:
        info = wallet.get_wallet_info(addr)
        print(f"     - {info['name']}: {addr}")
    print()
    
    print("=== TEST COMPLETE ===")
    print("Note: This is a test wallet. In the real application,")
    print("you would create wallets through the GUI interface.")

if __name__ == "__main__":
    test_wallet_functionality() 