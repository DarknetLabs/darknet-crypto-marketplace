import PyInstaller.__main__
import os
import sys

def build_executable():
    """Build the crypto marketplace as a Windows executable"""
    
    # PyInstaller arguments
    args = [
        'main.py',  # Main script
        '--onefile',  # Create single executable
        '--windowed',  # Hide console window
        '--name=CryptoMarketplace',  # Executable name
        '--icon=icon.ico',  # Icon (if available)
        '--add-data=crypto_rooms.py;.',  # Include crypto rooms module
        '--add-data=live_market_data.py;.',  # Include live market data module
        '--add-data=wallet_manager.py;.',  # Include wallet manager module
        '--add-data=ethereum_wallet.py;.',  # Include ethereum wallet module
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=json',
        '--hidden-import=threading',
        '--hidden-import=time',
        '--hidden-import=random',
        '--hidden-import=datetime',
        '--hidden-import=os',
        '--hidden-import=cryptography',
        '--hidden-import=secrets',
        '--hidden-import=hashlib',
        '--hidden-import=base64',
        '--clean',  # Clean cache
        '--noconfirm',  # Overwrite existing files
    ]
    
    # Remove icon argument if icon doesn't exist
    if not os.path.exists('icon.ico'):
        args = [arg for arg in args if not arg.startswith('--icon')]
    
    print("Building Crypto Marketplace executable...")
    print("This may take a few minutes...")
    
    try:
        PyInstaller.__main__.run(args)
        print("\nBuild completed successfully!")
        print("Executable created in: dist/CryptoMarketplace.exe")
        print("\nYou can now run the application by double-clicking CryptoMarketplace.exe")
        
    except Exception as e:
        print(f"Build failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_executable() 