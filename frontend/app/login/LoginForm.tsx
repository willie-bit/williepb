"use client";

import { useState, useTransition } from "react";

type LoginAction = (formData: FormData) => Promise<{ error?: string }>;

export default function LoginForm({ action }: { action: LoginAction }) {
  const [error, setError] = useState<string | null>(null);
  const [pending, start] = useTransition();

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    start(async () => {
      const res = await action(data);
      if (res?.error) setError(res.error);
    });
  };

  return (
    <form onSubmit={onSubmit}>
      <div className="form-row">
        <label htmlFor="email">이메일</label>
        <input id="email" name="email" type="email" required autoComplete="email" />
      </div>
      <div className="form-row">
        <label htmlFor="password">비밀번호</label>
        <input
          id="password"
          name="password"
          type="password"
          required
          minLength={8}
          autoComplete="current-password"
        />
      </div>
      {error ? <div className="error">{error}</div> : null}
      <button type="submit" disabled={pending} style={{ width: "100%", marginTop: 8 }}>
        {pending ? "로그인 중…" : "로그인"}
      </button>
    </form>
  );
}
