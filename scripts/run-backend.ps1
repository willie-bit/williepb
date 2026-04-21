# 백엔드 개발 서버 실행 (PowerShell)
$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\backend\.venv\Scripts\python.exe")) {
    Write-Host "❌ 가상환경이 없습니다. 먼저 .\scripts\setup.ps1 을 실행하세요." -ForegroundColor Red
    exit 1
}

Push-Location backend
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Pop-Location
