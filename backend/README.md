# williepb backend

FastAPI + SQLAlchemy 기반 가족 자산 관리 MVP.

## 빠른 시작

```bash
cd backend
cp .env.example .env
pip install -e ".[dev]"
williepb init-db
python -m scripts.seed      # 선택: 데모 가구 생성
uvicorn app.main:app --reload
```

API 문서는 `http://localhost:8000/docs` 에서 확인.

## 주요 엔드포인트

| Method | Path | 설명 |
|---|---|---|
| POST | `/api/v1/households` | 가구 생성 |
| POST | `/api/v1/members` | 구성원 추가 |
| POST | `/api/v1/accounts` | 계좌(기관·소유자) 등록 |
| POST | `/api/v1/assets` | 자산 수동 등록 |
| POST | `/api/v1/liabilities` | 부채 등록 |
| GET  | `/api/v1/dashboard/{household_id}` | 통합 대시보드 |
| GET  | `/api/v1/integrations` | 사용 가능한 어댑터 목록 |
| POST | `/api/v1/sync/household/{id}` | 시세 동기화 + 스냅샷 기록 |
| POST | `/api/v1/sync/account/{id}` | 특정 계좌 보유종목 동기화(CSV/API) |

## 연동 기관 (MVP)

- 은행: **KB국민은행**, **우리은행** (CSV 업로드)
- 증권사: **키움증권**, **NH투자증권** (CSV 업로드)
- 암호화폐: **업비트** (Open API)
- 시장시세: **KRX** (pykrx), **KRX 금시장**
- 부동산: **부동산원 R-ONE 지수** (+ 국토부 실거래가 보조)
- 환율: **한국은행 ECOS**

각 어댑터는 `app.integrations.base` 의 Protocol 을 구현하며
`app/integrations/bootstrap.py` 에서 레지스트리에 등록된다. 신규 기관 추가는
모듈 한 개 작성 + bootstrap 한 줄 추가로 끝난다.

## CSV 업로드 포맷 (MVP)

`POST /api/v1/sync/account/{id}` 의 `credentials.csv_path` 에 경로를 전달.

- KB: `계좌번호,계좌별칭,잔액,통화,기준일`
- 우리: `계좌번호,상품명,잔액,통화,기준일자`
- 키움: `계좌번호,종목코드,종목명,보유수량,매입평균가,기준일자`
- NH: `계좌번호,종목코드,종목명,잔고수량,매입단가,조회일자`

## 일 배치

```bash
williepb sync                 # 오늘자 시세 → 스냅샷 기록
williepb sync --on-date 2026-04-20
```

cron 예시:
```
30 1 * * *  cd /app && /usr/bin/williepb sync >> /var/log/williepb.log 2>&1
```

## 테스트

```bash
pytest
```

## 의존성 확장

실제 연동을 켤 때 추가로 필요한 패키지:

- `pip install "williepb-backend[market]"` — pykrx (KRX 국내주식/금 시세)
- `pip install pyjwt cryptography` — Upbit 본인계좌 인증
- `pip install "williepb-backend[postgres]"` — PostgreSQL 드라이버 (운영)

## 확장 포인트

- 증권사 OpenAPI 연동: `app/integrations/securities/kiwoom.py` 와
  `nh_invest.py` 의 주석을 참고. OAuth 토큰 저장소는 `Account.credentials`
  컬럼을 추가하고 KMS 봉투 암호화로 감싸면 된다.
- 마이데이터 중계사 연동: `app/integrations/banks/` 에 `mydata_broker.py`
  모듈을 신설, AccountAdapter Protocol 구현 후 bootstrap 에 등록.
- 세무 엔진: `app/services/tax/` 에 보유세/양도세 계산기를 추가할 자리를
  비워두었다 (설계서 §6 참고).
