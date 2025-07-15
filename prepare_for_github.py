#!/usr/bin/env python3
"""
Prepare files for GitHub upload
This script will copy only the necessary files to a clean directory for GitHub
"""

import os
import shutil
from pathlib import Path

def create_github_directory():
    """Create a clean directory with only the files needed for GitHub"""
    
    # Files to include in GitHub repository
    files_to_include = [
        # Main application files
        'terminal_main.py',
        'crypto_rooms.py', 
        'live_market_data.py',
        'wallet_manager.py',
        'ethereum_wallet.py',
        
        # Setup and launcher files
        'requirements_terminal.txt',
        'run_terminal.bat',
        'run_terminal.sh',
        
        # Documentation
        'README.md',
        'LICENSE',
        '.gitignore',
        
        # Optional helper files
        'install_terminal.py',
        'test_terminal.py',
        'TERMINAL_README.md',
        'TERMINAL_SETUP.md',
        'GITHUB_SETUP.md'
    ]
    
    # Create GitHub directory
    github_dir = Path('github_upload')
    if github_dir.exists():
        shutil.rmtree(github_dir)
    github_dir.mkdir()
    
    print("Creating GitHub upload directory...")
    
    # Copy files
    copied_count = 0
    for file_name in files_to_include:
        source_path = Path(file_name)
        if source_path.exists():
            shutil.copy2(source_path, github_dir / file_name)
            print(f"✅ Copied: {file_name}")
            copied_count += 1
        else:
            print(f"❌ Missing: {file_name}")
    
    print(f"\n📁 GitHub directory created: {github_dir.absolute()}")
    print(f"📄 Files copied: {copied_count}")
    
    # Create a simple upload guide
    upload_guide = f"""
# GitHub Upload Guide

Your files are ready in the 'github_upload' folder!

## Quick Upload Steps:

1. Go to GitHub.com and create a new repository named 'darknet-crypto-marketplace'
2. Make it PUBLIC
3. Don't initialize with README (you already have one)
4. Click "Create repository"

## Upload Method 1 (Easiest):
1. Go to your new repository
2. Click "uploading an existing file"
3. Drag and drop ALL files from the 'github_upload' folder
4. Add commit message: "Initial commit: Darknet Crypto Marketplace"
5. Click "Commit changes"

## Upload Method 2 (Git Commands):
```bash
cd github_upload
git init
git add .
git commit -m "Initial commit: Darknet Crypto Marketplace"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/darknet-crypto-marketplace.git
git push -u origin main
```

## After Upload:
1. Edit README.md on GitHub
2. Replace 'YOUR_USERNAME' with your actual GitHub username
3. Add topics: cryptocurrency, trading, terminal, python, blockchain

Your repository will be: https://github.com/YOUR_USERNAME/darknet-crypto-marketplace
"""
    
    with open(github_dir / 'UPLOAD_GUIDE.md', 'w') as f:
        f.write(upload_guide)
    
    print("📖 Upload guide created: UPLOAD_GUIDE.md")
    print("\n🎯 Next steps:")
    print("1. Open the 'github_upload' folder")
    print("2. Follow the instructions in UPLOAD_GUIDE.md")
    print("3. Upload all files to your new GitHub repository")

if __name__ == "__main__":
    create_github_directory() 