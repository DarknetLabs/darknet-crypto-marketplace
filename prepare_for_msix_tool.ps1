# Prepare files for MSIX Packaging Tool
Write-Host "=== Preparing Files for MSIX Packaging Tool ===" -ForegroundColor Green

# Create a clean directory structure
Write-Host "Creating clean directory structure..." -ForegroundColor Yellow

$outputDir = "MSIXPackagingTool_Ready"
if (Test-Path $outputDir) {
    Remove-Item $outputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $outputDir | Out-Null
New-Item -ItemType Directory -Path "$outputDir\Assets" | Out-Null

# Copy executable
if (Test-Path "dist\DarknetTerminal.exe") {
    Copy-Item "dist\DarknetTerminal.exe" "$outputDir\"
    Write-Host "✓ Copied DarknetTerminal.exe" -ForegroundColor Green
} elseif (Test-Path "dist\CryptoMarketplace.exe") {
    Copy-Item "dist\CryptoMarketplace.exe" "$outputDir\DarknetTerminal.exe"
    Write-Host "✓ Copied and renamed CryptoMarketplace.exe to DarknetTerminal.exe" -ForegroundColor Green
} else {
    Write-Host "✗ No executable found in dist folder" -ForegroundColor Red
}

# Copy assets
if (Test-Path "Assets") {
    Copy-Item "Assets\*" "$outputDir\Assets\" -Recurse -Force
    Write-Host "✓ Copied Assets folder" -ForegroundColor Green
} else {
    Write-Host "! No Assets folder found - you'll need to add images manually" -ForegroundColor Yellow
}

# Copy manifest
Copy-Item "appxmanifest.xml" "$outputDir\"
Write-Host "✓ Copied appxmanifest.xml" -ForegroundColor Green

Write-Host "`n=== Files Ready for MSIX Packaging Tool ===" -ForegroundColor Green
Write-Host "Directory: $outputDir" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Open MSIX Packaging Tool" -ForegroundColor White
Write-Host "2. Choose 'Create app package on this computer'" -ForegroundColor White
Write-Host "3. Point to: $outputDir\DarknetTerminal.exe" -ForegroundColor White
Write-Host "4. Use the appxmanifest.xml for package details" -ForegroundColor White
Write-Host "5. Build package as 'DarknetTerminal.msix'" -ForegroundColor White

# Show directory contents
Write-Host "`nPrepared files:" -ForegroundColor Cyan
Get-ChildItem $outputDir -Recurse | ForEach-Object { Write-Host "  $($_.FullName)" -ForegroundColor Gray } 