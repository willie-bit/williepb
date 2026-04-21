import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "williepb — 가족 자산 관리",
  description: "가족 자산 포트폴리오 대시보드",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
