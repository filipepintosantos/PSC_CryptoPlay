<#
Create a `.env` file for PSC CryptoPlay using a secure prompt.

Usage (PowerShell):
  .\scripts\create_env.ps1

This script will prompt for the CoinMarketCap API key (input hidden).
If you leave the prompt empty, it will copy `.env.example` to `.env` if present,
otherwise it will create an empty `.env` with the `COINMARKETCAP_API_KEY=` line.
#>

param ()

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$envPath = Join-Path $scriptRoot "..\.env"
$envExample = Join-Path $scriptRoot "..\.env.example"

if (Test-Path $envPath) {
    Write-Host ".env already exists at $envPath" -ForegroundColor Yellow
    Write-Host "If you want to overwrite it, remove the file and run this script again." -ForegroundColor Yellow
    return
}

Write-Host "Create .env for PSC CryptoPlay"

$secure = Read-Host "Enter CoinMarketCap API key (input hidden) - press Enter to skip" -AsSecureString
$key = [Runtime.InteropServices.Marshal]::PtrToStringBSTR([Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))

if ([string]::IsNullOrEmpty($key)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envPath
        Write-Host "Copied .env.example -> .env"
    } else {
        "COINMARKETCAP_API_KEY=" | Out-File -FilePath $envPath -Encoding ASCII
        Write-Host "Created empty .env (no .env.example found)"
    }
} else {
    "COINMARKETCAP_API_KEY=$key" | Out-File -FilePath $envPath -Encoding ASCII
    Write-Host ".env created at $envPath"
}
