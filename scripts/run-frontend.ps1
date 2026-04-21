# 프론트엔드 개발 서버 실행 (PowerShell)
$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\frontend\node_modules")) {
    Write-Host "❌ node_modules 가 없습니다. 먼저 .\scripts\setup.ps1 을 실행하세요." -ForegroundColor Red
    exit 1
}

Push-Location frontend
# 127.0.0.1 을 명시 (localhost 로 두면 Node 18+ 가 IPv6 ::1 으로 먼저 해석해서
# IPv4 만 듣는 백엔드와 어긋날 수 있음 — Windows 에서 'fetch failed' 의 흔한 원인)
$env:NEXT_PUBLIC_API_BASE = "http://127.0.0.1:8000"
npm run dev
Pop-Location
