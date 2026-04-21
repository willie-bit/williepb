# williepb frontend

Next.js App Router 기반 최소 대시보드. MVP 단계에서는 서버 컴포넌트에서
백엔드 `GET /api/v1/dashboard/:household_id` 를 호출하여 테이블로 렌더링한다.

## 실행

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
# 브라우저: http://localhost:3000/?household=1
```

## 확장 방향

- 차트: Recharts 또는 ECharts 를 추가해 파이/시계열 차트 붙이기
- 인증: NextAuth + 백엔드 JWT 연동
- 대시보드 세분화: 포트폴리오/부동산/세무 탭 분리 (설계서 §8 참고)
