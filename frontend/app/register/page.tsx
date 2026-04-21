import Link from "next/link";
import { redirect } from "next/navigation";
import { fetchMe, registerAction } from "@/lib/auth";
import RegisterForm from "./RegisterForm";

export default async function RegisterPage() {
  const me = await fetchMe();
  if (me) redirect("/dashboard");
  return (
    <div className="auth-page">
      <div className="card auth-card">
        <h1>회원가입</h1>
        <p className="sub">가구(Household)를 새로 만들고 관리자 권한을 얻습니다.</p>
        <RegisterForm action={registerAction} />
        <p style={{ marginTop: 16, fontSize: 13, color: "var(--muted)" }}>
          이미 계정이 있나요? <Link href="/login">로그인</Link>
        </p>
      </div>
    </div>
  );
}
