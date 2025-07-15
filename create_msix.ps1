# MSIX Packaging Script for Crypto Marketplace
# Run this script as Administrator

Write-Host "=== MSIX Packaging Script for Crypto Marketplace ===" -ForegroundColor Green

# Step 1: Create placeholder images using PowerShell
Write-Host "Step 1: Creating placeholder images..." -ForegroundColor Yellow

# Function to create a simple colored image
function Create-PlaceholderImage {
    param(
        [string]$Path,
        [int]$Width,
        [int]$Height,
        [string]$Color = "Blue"
    )
    
    $bitmap = New-Object System.Drawing.Bitmap $Width, $Height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $brush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::$Color)
    $graphics.FillRectangle($brush, 0, 0, $Width, $Height)
    
    # Add text
    $font = New-Object System.Drawing.Font "Arial", 12
    $textBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)
    $text = "Crypto`nMarketplace"
    $size = $graphics.MeasureString($text, $font)
    $x = ($Width - $size.Width) / 2
    $y = ($Height - $size.Height) / 2
    $graphics.DrawString($text, $font, $textBrush, $x, $y)
    
    $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
}

try {
    # Load System.Drawing assembly
    Add-Type -AssemblyName System.Drawing
    
    # Create placeholder images
    Create-PlaceholderImage "Assets\StoreLogo.png" 50 50 "DarkBlue"
    Create-PlaceholderImage "Assets\Square150x150Logo.png" 150 150 "DarkBlue"
    Create-PlaceholderImage "Assets\Square44x44Logo.png" 44 44 "DarkBlue"
    Create-PlaceholderImage "Assets\Wide310x150Logo.png" 310 150 "DarkBlue"
    Create-PlaceholderImage "Assets\SplashScreen.png" 620 300 "DarkBlue"
    
    Write-Host "✓ Placeholder images created successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not create images with System.Drawing. Creating empty files..." -ForegroundColor Yellow
    
    # Fallback: Create empty files
    @("StoreLogo.png", "Square150x150Logo.png", "Square44x44Logo.png", "Wide310x150Logo.png", "SplashScreen.png") | ForEach-Object {
        New-Item -Path "Assets\$_" -ItemType File -Force | Out-Null
    }
}

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

Write-Host "✓ Package directory prepared" -ForegroundColor Green

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
        Write-Host "✓ MSIX package created successfully: CryptoMarketplace.msix" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create MSIX package" -ForegroundColor Red
    }
} else {
    Write-Host "✗ MakeAppx.exe not found. Please install Windows SDK." -ForegroundColor Red
    Write-Host "Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/" -ForegroundColor Yellow
}

# Step 4: Alternative method using MSIX Packaging Tool
Write-Host "Step 4: Alternative - Using MSIX Packaging Tool..." -ForegroundColor Yellow
Write-Host "If MakeAppx failed, you can use the MSIX Packaging Tool GUI:" -ForegroundColor Cyan
Write-Host "1. Open 'MSIX Packaging Tool' from Start Menu" -ForegroundColor White
Write-Host "2. Click 'Create Package'" -ForegroundColor White
Write-Host "3. Select 'From existing installer'" -ForegroundColor White
Write-Host "4. Choose your executable: $packageDir\CryptoMarketplace.exe" -ForegroundColor White
Write-Host "5. Follow the wizard to create the package" -ForegroundColor White

Write-Host "`n=== Package Creation Complete ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the MSIX package locally" -ForegroundColor White
Write-Host "2. Sign the package with a code signing certificate" -ForegroundColor White
Write-Host "3. Submit to Microsoft Store" -ForegroundColor White 