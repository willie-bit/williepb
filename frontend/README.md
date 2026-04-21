# williepb frontend

Next.js App Router + Recharts. JWT 쿠키 인증 + 보호된 레이아웃.

## 실행

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

`http://localhost:3000/` 접속 → 로그인 화면으로 리다이렉트.
데모 계정 (seed 스크립트 실행 시): `dad@example.com` / `password1234`

## 페이지

| 경로 | 화면 |
|---|---|
| `/login`, `/register` | 인증 |
| `/dashboard` | KPI, 자산군 도넛, 순자산 시계열, 월별 P&L 바, 구성원 분해 |
| `/assets` | 자산 등록·조회·삭제 |
| `/liabilities` | 부채 등록·조회·삭제 |
| `/tax` | 재산세 / 종부세 / 양도세 시뮬레이션 |

## 구조

- `app/` — Next.js App Router 페이지. 서버 컴포넌트에서 쿠키 기반 JWT 로 백엔드 호출.
- `components/AppShell.tsx` + `Sidebar.tsx` — 인증 필요 레이아웃.
- `components/charts/*` — Recharts 기반 시각화.
- `lib/api.ts` — fetch wrapper, 쿠키에서 토큰 자동 첨부.
- `lib/auth.ts` — `loginAction`, `registerAction`, `logoutAction`, `requireUser` 서버 액션.
- `lib/actions.ts` — 자산·부채 Server Actions (revalidatePath 포함).

## 프로덕션 빌드

```bash
npm run build && npm run start
```
