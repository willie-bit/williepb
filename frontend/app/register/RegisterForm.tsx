"use client";

import { useState, useTransition } from "react";

type RegisterAction = (formData: FormData) => Promise<{ error?: string }>;

export default function RegisterForm({ action }: { action: RegisterAction }) {
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
      <div className="form-row inline">
        <div>
          <label htmlFor="display_name">본인 이름</label>
          <input id="display_name" name="display_name" required maxLength={80} />
        </div>
        <div>
          <label htmlFor="household_name">가구 이름</label>
          <input
            id="household_name"
            name="household_name"
            required
            maxLength={120}
            placeholder="예: Lee 가족"
          />
        </div>
      </div>
      <div className="form-row">
        <label htmlFor="email">이메일</label>
        <input id="email" name="email" type="email" required autoComplete="email" />
      </div>
      <div className="form-row">
        <label htmlFor="password">비밀번호 (8자 이상)</label>
        <input
          id="password"
          name="password"
          type="password"
          required
          minLength={8}
          maxLength={72}
          autoComplete="new-password"
        />
      </div>
      {error ? <div className="error">{error}</div> : null}
      <button type="submit" disabled={pending} style={{ width: "100%", marginTop: 8 }}>
        {pending ? "가입 중…" : "가입하기"}
      </button>
    </form>
  );
}
