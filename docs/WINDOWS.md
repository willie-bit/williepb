# Windows 에서 실행하기 (VS Code)

## 0) 사전 설치

| 도구 | 설치 링크 | 확인 명령 |
|---|---|---|
| Python 3.11+ | <https://www.python.org/downloads/windows/> (설치 시 **"Add python.exe to PATH"** 체크 필수) | `python --version` |
| Node.js 20+ | <https://nodejs.org/en/download> | `node --version` |
| Git | <https://git-scm.com/download/win> | `git --version` |
| VS Code | <https://code.visualstudio.com/> | |

PowerShell에서 위 4개 명령이 모두 정상 출력돼야 합니다.

## 1) 프로젝트 받기

### 방법 A — git clone (권장)
```powershell
cd $HOME\Documents
git clone https://github.com/willie-bit/williepb.git
cd williepb
git checkout claude/family-asset-management-jkMFn
```

### 방법 B — GitHub 에서 ZIP 다운로드
1. 브라우저에서 `https://github.com/willie-bit/williepb` 접속
2. 브랜치 드롭다운에서 **`claude/family-asset-management-jkMFn`** 선택
3. 녹색 **`Code`** 버튼 → **`Download ZIP`**
4. 다운로드된 zip 을 `C:\Users\<사용자>\Documents\williepb` 같은 **짧고 한글·공백 없는 경로**로 압축 해제
5. 압축 푼 폴더 안에 `backend`, `frontend`, `docs`, `README.md` 가 보이는지 확인

## 2) VS Code 로 열기

```powershell
cd <프로젝트 루트>
code .
```

또는 VS Code → `File → Open Folder…` → `backend`와 `frontend`가 같이 보이는 폴더 선택.
"Do you trust the authors?" 팝업에 **Yes** 클릭.

첫 실행 시 우측 하단에 확장 추천(Python / Ruff / Prettier / ESLint)이 뜨면 모두 설치.

## 3) 원샷 설치 — VS Code 태스크 사용

VS Code 에서 **`Ctrl+Shift+P`** → `Tasks: Run Task` → **`Setup (install everything)`** 선택.

자동으로:
- `backend\.venv` 가상환경 생성
- 백엔드 패키지 설치 (`pip install -e ".[dev]"`)
- SQLite DB 초기화 + 데모 데이터 주입
- JWT 시크릿 생성 후 `backend\.env` 에 기록
- 프론트엔드 `npm install`

> **막히는 경우:** 최초 1회만 PowerShell 실행 정책을 허용해야 합니다.
> 관리자 권한 PowerShell 에서:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
> ```

## 4) 실행

### 방법 A — VS Code 태스크
`Ctrl+Shift+P` → `Tasks: Run Task` → **`Start All`**  
백엔드와 프론트엔드가 각각 전용 터미널 패널에서 기동됩니다.

### 방법 B — 터미널에서 직접
VS Code 에서 **``Ctrl+` ``** (백틱) 으로 터미널 2개를 열고:

**터미널 1 (백엔드):**
```powershell
.\scripts\run-backend.ps1
```

**터미널 2 (프론트엔드):**
```powershell
.\scripts\run-frontend.ps1
```

## 5) 브라우저 접속

- 앱: <http://localhost:3000>
- API 문서: <http://localhost:8000/docs>

**데모 로그인:** `dad@example.com` / `password1234`

## 자주 묻는 에러

### `ExecutionPolicy` / `스크립트 로딩이 사용 안 함`
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

### `python 용어를 인식할 수 없습니다`
Python 이 설치되지 않았거나 PATH 에 없습니다. 재설치 시 **"Add python.exe to PATH"** 체크 후
PowerShell 을 **새로 열어** 확인.

### `Microsoft Store 를 열어 Python 을 설치하세요` 팝업
Windows 기본 상태에서 `python` 명령이 Store alias 만 가리키는 경우입니다.
`설정 → 앱 → 고급 앱 설정 → 앱 실행 별칭` 에서 `python.exe`, `python3.exe` 두 항목을 **끄고**,
python.org 에서 설치한 진짜 Python 을 사용하도록 합니다.

### `포트 8000/3000 이 이미 사용 중`
```powershell
# 어떤 프로세스가 쓰는지 확인
Get-NetTCPConnection -LocalPort 8000
Get-NetTCPConnection -LocalPort 3000
```
해당 프로세스 종료 후 다시 실행.

### `npm install` 이 매우 느림
프로젝트를 `OneDrive` 로 동기화되는 경로 밑에 두지 마세요. `Documents\williepb` 는 보통 OneDrive
대상이 됩니다. `C:\dev\williepb` 같은 OneDrive 영향 없는 경로가 빠릅니다.

### bcrypt 또는 cryptography 설치 실패
```powershell
.\backend\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\backend\.venv\Scripts\python.exe -m pip install --force-reinstall bcrypt cryptography cffi
```

## 테스트 실행 (선택)
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```
24개 테스트가 모두 통과하면 정상.
