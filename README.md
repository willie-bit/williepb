# williepb — 가족 자산 관리 서비스

가족 구성원 전원의 자산(부동산·주식·연금·현금·암호화폐·금·자동차·실물)과 부채(대출·카드)를
하나의 뷰로 통합하고, 매일 자동 갱신되는 시세와 포트폴리오·세무 인사이트를 제공합니다.

현재 단계: **MVP 프로토타입** — FastAPI 백엔드 + Next.js 프론트엔드.

## 구성

| 디렉토리 | 역할 |
|---|---|
| [`backend/`](./backend/README.md) | FastAPI, SQLAlchemy, 어댑터 레지스트리, 일 배치 CLI |
| [`frontend/`](./frontend/README.md) | Next.js(App Router) 대시보드 — SSR 로 백엔드 호출 |
| [`docs/`](./docs/INITIAL_DESIGN.md) | 초안 설계서 (v0.1) / Windows 설치 가이드 |
| [`scripts/`](./scripts/setup.ps1) | Windows 원샷 설치·실행 스크립트 |
| [`.vscode/`](./.vscode/tasks.json) | VS Code 태스크(Setup / Start All) |

## MVP 연동 범위

- 은행: **KB국민은행**, **우리은행** (CSV 업로드 → 잔액 등록)
- 증권사: **키움증권**, **NH투자증권** (CSV 업로드 → 보유종목 등록)
- 암호화폐: **업비트** Open API (잔고 + 시세)
- 시장시세: **KRX** (pykrx), **KRX 금시장**
- 부동산: **부동산원 R-ONE 지수** + **국토부 실거래가** 보조
- 환율: **한국은행 ECOS**

신규 기관 추가는 `app/integrations/` 에 어댑터 모듈 하나 + `bootstrap.py`
한 줄 등록으로 끝나도록 Protocol 기반으로 설계했습니다.

## 로컬에서 한 번에 띄우기

### Windows (VS Code)
**완전한 단계별 가이드: [`docs/WINDOWS.md`](./docs/WINDOWS.md)**

요약:
1. Python 3.11+, Node.js 20+, Git 설치
2. 저장소 클론 후 VS Code 로 폴더 열기
3. `Ctrl+Shift+P` → `Tasks: Run Task` → **`Setup (install everything)`**
4. `Ctrl+Shift+P` → `Tasks: Run Task` → **`Start All`**
5. 브라우저: <http://localhost:3000> (`dad@example.com` / `password1234`)

### macOS / Linux
```bash
# 백엔드
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m app.cli init-db
python -m scripts.seed
export WILLIEPB_JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
uvicorn app.main:app --reload     # http://localhost:8000/docs

# 프론트엔드 (다른 터미널)
cd frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

### 도커 (Postgres 포함)
```bash
docker compose up --build
```

## 일 배치

```bash
williepb sync                     # 오늘자 시세 동기화 + 가구별 스냅샷 저장
```

cron 등록 예시는 `backend/README.md` 참고.

## 다음 단계

- 증권사 REST OpenAPI 연동 (본인계좌 자동 잔고 조회)
- 마이데이터 중계사 파트너 PoC
- 세무 엔진(보유세·양도세·금융소득종합과세)
- 인증(NextAuth + JWT) 및 가족 초대 플로우
- 차트 UI (Recharts/ECharts)
- Alembic 마이그레이션 도입

자세한 백로그는 [`docs/INITIAL_DESIGN.md`](./docs/INITIAL_DESIGN.md) §11 로드맵 참고.
