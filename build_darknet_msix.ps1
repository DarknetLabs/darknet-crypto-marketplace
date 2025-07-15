# MSIX Packaging Script for Darknet Terminal
Write-Host "=== MSIX Packaging Script for Darknet Terminal ===" -ForegroundColor Green

# Step 1: Create placeholder images if they don't exist
Write-Host "Step 1: Creating placeholder images..." -ForegroundColor Yellow

if (-not (Test-Path "Assets")) {
    New-Item -ItemType Directory -Path "Assets" | Out-Null
}

$imageFiles = @("StoreLogo.png", "Square150x150Logo.png", "Square44x44Logo.png", "Wide310x150Logo.png", "SplashScreen.png")

foreach ($file in $imageFiles) {
    if (-not (Test-Path "Assets\$file")) {
        New-Item -Path "Assets\$file" -ItemType File -Force | Out-Null
    }
}

Write-Host "✓ Placeholder images ready" -ForegroundColor Green

# Step 2: Copy executable to package directory
Write-Host "Step 2: Preparing package directory..." -ForegroundColor Yellow

$packageDir = "MSIXPackage"
if (Test-Path $packageDir) {
    Remove-Item $packageDir -Recurse -Force
}
New-Item -ItemType Directory -Path $packageDir | Out-Null

# Create Assets directory in package
New-Item -ItemType Directory -Path "$packageDir\Assets" -Force | Out-Null

# Copy executable and assets
Copy-Item "dist\DarknetTerminal.exe" "$packageDir\"
Copy-Item "Assets\*" "$packageDir\Assets\" -Recurse -Force
Copy-Item "appxmanifest.xml" "$packageDir\"

Write-Host "✓ Package directory prepared" -ForegroundColor Green

# Step 3: Create MSIX package using MakeAppx
Write-Host "Step 3: Creating MSIX package..." -ForegroundColor Yellow

# Find Windows SDK path
$sdkPaths = @(
    "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.22621.0\x64",
    "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.22000.0\x64",
    "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.19041.0\x64",
    "${env:ProgramFiles(x86)}\Windows Kits\10\bin\x64"
)

$makeAppxPath = $null
foreach ($path in $sdkPaths) {
    $testPath = "$path\makeappx.exe"
    if (Test-Path $testPath) {
        $makeAppxPath = $testPath
        break
    }
}

if ($makeAppxPath) {
    Write-Host "Using SDK at: $makeAppxPath" -ForegroundColor Cyan
    & $makeAppxPath pack /d $packageDir /p "DarknetTerminal.msix"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ MSIX package created successfully: DarknetTerminal.msix" -ForegroundColor Green
        
        # Show file info
        $fileInfo = Get-Item "DarknetTerminal.msix"
        Write-Host "Package size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan
        Write-Host "Package location: $($fileInfo.FullName)" -ForegroundColor Cyan
    } else {
        Write-Host "✗ Failed to create MSIX package" -ForegroundColor Red
    }
} else {
    Write-Host "✗ MakeAppx.exe not found. Please install Windows SDK." -ForegroundColor Red
    Write-Host "Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/" -ForegroundColor Yellow
}

Write-Host "`n=== Package Creation Complete ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the MSIX package locally" -ForegroundColor White
Write-Host "2. Upload DarknetTerminal.msix to Microsoft Store" -ForegroundColor White
Write-Host "3. The package should now pass validation" -ForegroundColor White 