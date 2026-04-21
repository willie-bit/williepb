"use client";

import { useState, useTransition } from "react";
import { createLiabilityAction } from "@/lib/actions";
import type { Member } from "@/lib/types";

type Props = {
  householdId: number;
  members: Member[];
  typeLabels: Record<string, string>;
};

export function LiabilityForm({ householdId, members, typeLabels }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [pending, start] = useTransition();

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    start(async () => {
      const res = await createLiabilityAction(data);
      if (res?.error) setError(res.error);
      else {
        setError(null);
        form.reset();
      }
    });
  };

  return (
    <form onSubmit={onSubmit}>
      <input type="hidden" name="household_id" value={householdId} />
      <div className="form-row inline">
        <div>
          <label htmlFor="liability_type">부채 종류</label>
          <select id="liability_type" name="liability_type" defaultValue="MORTGAGE">
            {Object.entries(typeLabels).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="owner_member_id">채무자</label>
          <select id="owner_member_id" name="owner_member_id" required>
            {members.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="form-row">
        <label htmlFor="label">이름</label>
        <input id="label" name="label" required maxLength={160} placeholder="예: 주택담보대출" />
      </div>
      <div className="form-row inline">
        <div>
          <label htmlFor="principal">원금 (KRW)</label>
          <input id="principal" name="principal" type="number" step="1" required />
        </div>
        <div>
          <label htmlFor="balance">잔액 (KRW)</label>
          <input id="balance" name="balance" type="number" step="1" required />
        </div>
      </div>
      <div className="form-row inline">
        <div>
          <label htmlFor="interest_rate">금리 (예: 0.042 = 4.2%)</label>
          <input id="interest_rate" name="interest_rate" type="number" step="0.0001" />
        </div>
        <div>
          <label htmlFor="rate_type">금리 유형</label>
          <select id="rate_type" name="rate_type" defaultValue="FIXED">
            <option value="FIXED">고정</option>
            <option value="FLOAT">변동</option>
          </select>
        </div>
      </div>
      <div className="form-row inline">
        <div>
          <label htmlFor="start_date">개시일</label>
          <input id="start_date" name="start_date" type="date" />
        </div>
        <div>
          <label htmlFor="maturity_date">만기일</label>
          <input id="maturity_date" name="maturity_date" type="date" />
        </div>
      </div>
      <div className="form-row">
        <label htmlFor="institution_code">기관 코드 (선택)</label>
        <input id="institution_code" name="institution_code" placeholder="예: kb_kookmin" />
      </div>
      {error ? <div className="error">{error}</div> : null}
      <button type="submit" disabled={pending}>
        {pending ? "등록 중…" : "부채 추가"}
      </button>
    </form>
  );
}
