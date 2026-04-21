"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { CurrentUser } from "@/lib/types";

type Props = {
  me: CurrentUser;
  onLogout: () => Promise<void>;
};

const items: { href: string; label: string }[] = [
  { href: "/dashboard", label: "대시보드" },
  { href: "/assets", label: "자산" },
  { href: "/liabilities", label: "부채" },
  { href: "/tax", label: "세무 시뮬" },
];

export default function Sidebar({ me, onLogout }: Props) {
  const pathname = usePathname();
  return (
    <aside className="sidebar" style={{ display: "flex", flexDirection: "column" }}>
      <div className="brand">💼 williepb</div>
      <nav>
        {items.map((i) => (
          <Link
            key={i.href}
            href={i.href}
            className={pathname?.startsWith(i.href) ? "active" : ""}
          >
            {i.label}
          </Link>
        ))}
      </nav>
      <form action={onLogout} style={{ marginTop: "auto" }}>
        <div className="user-box">
          <strong>{me.display_name ?? me.email}</strong>
          <div>{me.household_name}</div>
          <div className="badge" style={{ marginTop: 6 }}>{me.role}</div>
        </div>
        <button type="submit" className="ghost" style={{ width: "100%", marginTop: 12 }}>
          로그아웃
        </button>
      </form>
    </aside>
  );
}
