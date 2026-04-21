# williepb backend

FastAPI + SQLAlchemy. JWT 인증, 세무 시뮬레이션, 일별 스냅샷을 포함한 MVP.

## 빠른 시작

```bash
cd backend
cp .env.example .env
# WILLIEPB_JWT_SECRET 는 32바이트 이상 무작위 문자열로 설정
pip install -e ".[dev]"
williepb init-db
python -m scripts.seed      # 데모 가구 + 데모 로그인 계정 생성
uvicorn app.main:app --reload
```

데모 로그인: `dad@example.com` / `password1234`

API 문서는 `http://localhost:8000/docs`.

## 인증

- `POST /api/v1/auth/register` — 이메일/비밀번호/가구명 → JWT
- `POST /api/v1/auth/login` — JWT
- `GET  /api/v1/auth/me` — 현재 사용자 + 가구/구성원 정보

모든 데이터 엔드포인트는 `Authorization: Bearer <token>` 혹은 `williepb_token`
쿠키를 요구합니다. 각 사용자는 자신의 가구에 한해 접근 가능 (`AuthContext` 의존성).

## 자산·부채·대시보드 API

| Method | Path | 설명 |
|---|---|---|
| GET  | `/api/v1/dashboard` | 내 가구 대시보드 |
| GET  | `/api/v1/timeseries/net-worth?days=90` | 순자산 시계열 |
| GET/POST/PATCH/DELETE | `/api/v1/assets` | 자산 CRUD |
| GET/POST/DELETE | `/api/v1/liabilities` | 부채 CRUD |
| GET  | `/api/v1/members` | 가구 구성원 |
| POST | `/api/v1/sync/household` | 시세 동기화 + 스냅샷 |

## 세무 시뮬레이션 API

| Method | Path | 설명 |
|---|---|---|
| POST | `/api/v1/tax/property` | 재산세 (주택분 + 도시지역분 + 지방교육세) |
| POST | `/api/v1/tax/comprehensive` | 종합부동산세 (가구 합산) |
| POST | `/api/v1/tax/capital-gains` | 양도소득세 (주택, 단기/장기/중과) |

세율·공제는 2024년 기준 단순화 버전입니다. `app/services/tax/` 의 브래킷 상수를
연도별로 업데이트할 수 있습니다.

## 연동 기관 (MVP 어댑터)

- 은행: **KB국민**, **우리** — CSV 업로드
- 증권사: **키움**, **NH투자** — CSV 업로드
- 암호화폐: **업비트** Open API
- 시장: KRX (pykrx), KRX 금시장
- 환율: 한국은행 ECOS
- 부동산: 부동산원 R-ONE 지수 + 국토부 실거래가 (골격)

각 어댑터 파일 주석에 실제 API 연동 전환 경로를 정리. 신규 기관은 모듈 한 개 +
`app/integrations/bootstrap.py` 한 줄 등록으로 추가.

## 일 배치

```bash
williepb sync                     # 오늘자 시세 → 가구별 스냅샷
```

## 테스트

```bash
pytest
```

24개 (valuation, aggregation, P&L, 어댑터 CSV 파싱, 세무 3종, 인증 플로우).
