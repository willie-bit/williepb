"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { apiBase } from "./api";
import type { CurrentUser } from "./types";

const COOKIE_NAME = "williepb_token";
const COOKIE_MAX_AGE = 60 * 60 * 24 * 7; // 7d, matches backend JWT TTL

type TokenResponse = { access_token: string };

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const msg =
      data && typeof data === "object" && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : "요청이 실패했습니다";
    throw new Error(msg);
  }
  return data as T;
}

export async function loginAction(formData: FormData): Promise<{ error?: string }> {
  const email = String(formData.get("email") ?? "");
  const password = String(formData.get("password") ?? "");
  try {
    const { access_token } = await post<TokenResponse>("/api/v1/auth/login", {
      email,
      password,
    });
    setTokenCookie(access_token);
  } catch (err) {
    return { error: err instanceof Error ? err.message : "로그인 실패" };
  }
  redirect("/dashboard");
}

export async function registerAction(formData: FormData): Promise<{ error?: string }> {
  const email = String(formData.get("email") ?? "");
  const password = String(formData.get("password") ?? "");
  const display_name = String(formData.get("display_name") ?? "");
  const household_name = String(formData.get("household_name") ?? "");
  try {
    const { access_token } = await post<TokenResponse>("/api/v1/auth/register", {
      email,
      password,
      display_name,
      household_name,
    });
    setTokenCookie(access_token);
  } catch (err) {
    return { error: err instanceof Error ? err.message : "가입 실패" };
  }
  redirect("/dashboard");
}

export async function logoutAction(): Promise<void> {
  cookies().delete(COOKIE_NAME);
  redirect("/login");
}

function setTokenCookie(token: string): void {
  cookies().set({
    name: COOKIE_NAME,
    value: token,
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: COOKIE_MAX_AGE,
    secure: process.env.NODE_ENV === "production",
  });
}

export async function fetchMe(): Promise<CurrentUser | null> {
  const token = cookies().get(COOKIE_NAME)?.value;
  if (!token) return null;
  try {
    const res = await fetch(`${apiBase()}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return (await res.json()) as CurrentUser;
  } catch {
    return null;
  }
}

export async function requireUser(): Promise<CurrentUser> {
  const me = await fetchMe();
  if (!me) redirect("/login");
  return me;
}
