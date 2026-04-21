import Link from "next/link";
import { redirect } from "next/navigation";
import { fetchMe, loginAction } from "@/lib/auth";
import LoginForm from "./LoginForm";

export default async function LoginPage() {
  const me = await fetchMe();
  if (me) redirect("/dashboard");
  return (
    <div className="auth-page">
      <div className="card auth-card">
        <h1>로그인</h1>
        <p className="sub">williepb 가족 자산 관리</p>
        <LoginForm action={loginAction} />
        <p style={{ marginTop: 16, fontSize: 13, color: "var(--muted)" }}>
          계정이 없나요? <Link href="/register">회원가입</Link>
        </p>
      </div>
    </div>
  );
}
