@echo off
echo Building DARKNET CRYPTO MARKETPLACE executable...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Building executable...
python build_exe.py
echo.
echo Build complete! Check the dist folder for CryptoMarketplace.exe
pause 