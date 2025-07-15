# MSIX Packaging Script for Crypto Marketplace
Write-Host "=== MSIX Packaging Script for Crypto Marketplace ===" -ForegroundColor Green

# Step 1: Create placeholder images
Write-Host "Step 1: Creating placeholder images..." -ForegroundColor Yellow

$imageFiles = @("StoreLogo.png", "Square150x150Logo.png", "Square44x44Logo.png", "Wide310x150Logo.png", "SplashScreen.png")

foreach ($file in $imageFiles) {
    New-Item -Path "Assets\$file" -ItemType File -Force | Out-Null
}

Write-Host "Placeholder images created successfully" -ForegroundColor Green

# Step 2: Copy executable to package directory
Write-Host "Step 2: Preparing package directory..." -ForegroundColor Yellow

$packageDir = "MSIXPackage"
if (Test-Path $packageDir) {
    Remove-Item $packageDir -Recurse -Force
}
New-Item -ItemType Directory -Path $packageDir | Out-Null

# Copy executable and assets
Copy-Item "dist\CryptoMarketplace.exe" "$packageDir\"
Copy-Item "Assets\*" "$packageDir\Assets\" -Recurse -Force
Copy-Item "appxmanifest.xml" "$packageDir\"

Write-Host "Package directory prepared" -ForegroundColor Green

# Step 3: Create MSIX package using MakeAppx
Write-Host "Step 3: Creating MSIX package..." -ForegroundColor Yellow

$sdkPath = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.22000.0\x64"
if (-not (Test-Path $sdkPath)) {
    $sdkPath = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.19041.0\x64"
}
if (-not (Test-Path $sdkPath)) {
    $sdkPath = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\x64"
}

$makeAppxPath = "$sdkPath\makeappx.exe"
if (Test-Path $makeAppxPath) {
    & $makeAppxPath pack /d $packageDir /p "CryptoMarketplace.msix"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MSIX package created successfully: CryptoMarketplace.msix" -ForegroundColor Green
    } else {
        Write-Host "Failed to create MSIX package" -ForegroundColor Red
    }
} else {
    Write-Host "MakeAppx.exe not found. Please install Windows SDK." -ForegroundColor Red
    Write-Host "Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/" -ForegroundColor Yellow
}

Write-Host "Package Creation Complete" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the MSIX package locally" -ForegroundColor White
Write-Host "2. Sign the package with a code signing certificate" -ForegroundColor White
Write-Host "3. Submit to Microsoft Store" -ForegroundColor White 