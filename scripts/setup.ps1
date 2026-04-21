# williepb — Windows 원샷 설치 스크립트 (PowerShell)
# 사용: VS Code 터미널에서  .\scripts\setup.ps1
# 사전 요구: Python 3.11+, Node.js 20+, (선택) git.
#
# 1) 백엔드 가상환경 + 패키지 설치
# 2) DB 초기화 + 데모 데이터 주입
# 3) JWT 시크릿 생성 후 backend\.env 에 저장
# 4) 프론트엔드 npm 의존성 설치

$ErrorActionPreference = "Stop"

function Step($msg) {
    Write-Host ""
    Write-Host "▶ $msg" -ForegroundColor Cyan
}

# 프로젝트 루트에서 실행됐는지 확인
if (-not (Test-Path ".\backend") -or -not (Test-Path ".\frontend")) {
    Write-Host "❌ backend / frontend 폴더가 보이지 않습니다. 프로젝트 루트에서 실행하세요." -ForegroundColor Red
    exit 1
}

# Python 확인
Step "Python 확인"
try {
    $pyver = & python --version 2>&1
    Write-Host "   $pyver"
} catch {
    Write-Host "❌ python 이 PATH에 없습니다. python.org 에서 설치 후 'Add to PATH' 체크." -ForegroundColor Red
    exit 1
}

# Node 확인
Step "Node.js 확인"
try {
    $nodever = & node --version 2>&1
    Write-Host "   node $nodever"
} catch {
    Write-Host "❌ node 가 PATH에 없습니다. nodejs.org 에서 설치하세요." -ForegroundColor Red
    exit 1
}

# ── 백엔드 ──
Step "백엔드 가상환경 생성 (backend\.venv)"
Push-Location backend
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
$venvPython = ".\.venv\Scripts\python.exe"

Step "백엔드 패키지 설치 (pip install -e .[dev])"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -e ".[dev]"

Step "DB 초기화 + 데모 데이터 주입"
& $venvPython -m app.cli init-db
& $venvPython -m scripts.seed

Step "JWT 시크릿 생성 후 backend\.env 저장"
$secret = & $venvPython -c "import secrets; print(secrets.token_urlsafe(48))"
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    } else {
        New-Item -ItemType File -Path ".env" | Out-Null
    }
}
# 기존 WILLIEPB_JWT_SECRET 라인이 있으면 교체, 없으면 추가
$envText = Get-Content .env -Raw -ErrorAction SilentlyContinue
if ($null -eq $envText) { $envText = "" }
if ($envText -match "^WILLIEPB_JWT_SECRET=.*$") {
    $envText = [regex]::Replace($envText, "(?m)^WILLIEPB_JWT_SECRET=.*$", "WILLIEPB_JWT_SECRET=$secret")
} else {
    if ($envText -and -not $envText.EndsWith("`n")) { $envText += "`n" }
    $envText += "WILLIEPB_JWT_SECRET=$secret`n"
}
Set-Content -Path .env -Value $envText -NoNewline
Pop-Location

# ── 프론트엔드 ──
Step "프론트엔드 npm install"
Push-Location frontend
npm install
Pop-Location

Write-Host ""
Write-Host "✅ 설치 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "실행 방법:" -ForegroundColor Yellow
Write-Host "  터미널 1:  .\scripts\run-backend.ps1"
Write-Host "  터미널 2:  .\scripts\run-frontend.ps1"
Write-Host ""
Write-Host "또는 VS Code 에서 Ctrl+Shift+P → 'Tasks: Run Task' → 'Start All'" -ForegroundColor Yellow
Write-Host ""
Write-Host "브라우저: http://localhost:3000  (로그인: dad@example.com / password1234)"
