@echo off
title Prepare Files for GitHub Upload
color 0A
cls

echo Creating GitHub upload directory...
echo.

REM Create github_upload directory
if exist "github_upload" rmdir /s /q "github_upload"
mkdir "github_upload"

echo Copying files to github_upload folder...

REM Copy main application files
copy "terminal_main.py" "github_upload\" >nul 2>&1
copy "crypto_rooms.py" "github_upload\" >nul 2>&1
copy "live_market_data.py" "github_upload\" >nul 2>&1
copy "wallet_manager.py" "github_upload\" >nul 2>&1
copy "ethereum_wallet.py" "github_upload\" >nul 2>&1

REM Copy setup files
copy "requirements_terminal.txt" "github_upload\" >nul 2>&1
copy "run_terminal.bat" "github_upload\" >nul 2>&1
copy "run_terminal.sh" "github_upload\" >nul 2>&1

REM Copy documentation
copy "README.md" "github_upload\" >nul 2>&1
copy "LICENSE" "github_upload\" >nul 2>&1
copy ".gitignore" "github_upload\" >nul 2>&1

REM Copy helper files
copy "install_terminal.py" "github_upload\" >nul 2>&1
copy "test_terminal.py" "github_upload\" >nul 2>&1
copy "TERMINAL_README.md" "github_upload\" >nul 2>&1
copy "TERMINAL_SETUP.md" "github_upload\" >nul 2>&1
copy "GITHUB_SETUP.md" "github_upload\" >nul 2>&1

echo.
echo Files copied to github_upload folder!
echo.
echo Next steps:
echo 1. Go to GitHub.com and create a new repository
echo 2. Name it: darknet-crypto-marketplace
echo 3. Make it PUBLIC
echo 4. Don't initialize with README
echo 5. Click "Create repository"
echo 6. Click "uploading an existing file"
echo 7. Drag and drop ALL files from github_upload folder
echo 8. Add commit message: "Initial commit: Darknet Crypto Marketplace"
echo 9. Click "Commit changes"
echo.
echo Your repository will be ready!
echo.
pause 