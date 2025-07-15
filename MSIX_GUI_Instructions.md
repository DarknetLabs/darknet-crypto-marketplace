# MSIX Packaging Tool GUI Instructions

## Step-by-Step Process

### 1. Open MSIX Packaging Tool
- Press `Windows + R`
- Type: `msixpackagingtool`
- Press Enter
- Or search "MSIX Packaging Tool" in Start Menu

### 2. Create Package
- Click **"Create Package"**
- Select **"From existing installer"**
- Click **"Next"**

### 3. Select Installer
- Click **"Browse"**
- Navigate to: `C:\Users\HP\OneDrive\Documents\Darknet\MSIXPackage\CryptoMarketplace.exe`
- Select the file
- Click **"Next"**

### 4. Package Information
- **Package Display Name:** Crypto Marketplace
- **Publisher Name:** Your Name (or your company name)
- **Package Name:** CryptoMarketplace
- **Version:** 1.0.0.0
- Click **"Next"**

### 5. Capabilities
- Check these capabilities:
  - ✅ **runFullTrust** (Required for desktop apps)
  - ✅ **internetClient** (For crypto trading)
  - ✅ **internetClientServer** (For chat functionality)
  - ✅ **privateNetworkClientServer** (For local network)
  - ✅ **documentsLibrary** (For wallet files)
  - ✅ **picturesLibrary** (For any images)
  - ✅ **allowElevation** (For admin operations)
- Click **"Next"**

### 6. Assets
- **Store Logo:** Browse to `Assets\StoreLogo.png`
- **Square 150x150 Logo:** Browse to `Assets\Square150x150Logo.png`
- **Square 44x44 Logo:** Browse to `Assets\Square44x44Logo.png`
- **Wide 310x150 Logo:** Browse to `Assets\Wide310x150Logo.png`
- **Splash Screen:** Browse to `Assets\SplashScreen.png`
- Click **"Next"**

### 7. Package Settings
- **Output Location:** Choose where to save the MSIX file
- **Package Name:** CryptoMarketplace.msix
- Click **"Create"**

### 8. Wait for Completion
- The tool will analyze your executable
- It will create the MSIX package
- This may take several minutes

### 9. Success!
- You'll see "Package created successfully"
- Your MSIX file is ready

## Next Steps After Creating MSIX

### 1. Test Locally
```powershell
# Install the package locally for testing
Add-AppxPackage -Path "CryptoMarketplace.msix"
```

### 2. Code Signing (Required for Store)
- Purchase a code signing certificate from:
  - DigiCert
  - Sectigo
  - GlobalSign
  - Or use Microsoft's certificate for Store apps

### 3. Sign the Package
```powershell
# Sign with your certificate
SignTool sign /f "your-certificate.pfx" /p "password" /t "http://timestamp.digicert.com" "CryptoMarketplace.msix"
```

### 4. Submit to Microsoft Store
- Go to https://partner.microsoft.com/dashboard
- Create a developer account ($19/year)
- Submit your signed MSIX package
- Provide app description, screenshots, etc.

## Troubleshooting

### Common Issues:
1. **"MakeAppx not found"** - Install Windows SDK
2. **"Certificate required"** - Purchase code signing certificate
3. **"Capabilities not allowed"** - Remove restricted capabilities for Store
4. **"App doesn't start"** - Check if all dependencies are included

### Alternative: Use Advanced Installer
- Download Advanced Installer (free trial)
- Import your executable
- Export as MSIX
- Often easier than manual process 