# 프론트엔드 개발 서버 실행 (PowerShell)
$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\frontend\node_modules")) {
    Write-Host "❌ node_modules 가 없습니다. 먼저 .\scripts\setup.ps1 을 실행하세요." -ForegroundColor Red
    exit 1
}

Push-Location frontend
$env:NEXT_PUBLIC_API_BASE = "http://localhost:8000"
npm run dev
Pop-Location
