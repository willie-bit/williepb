import { cookies } from "next/headers";

// Default to 127.0.0.1 (not "localhost") because Node 18+ on Windows resolves
// "localhost" to IPv6 (::1) first, and the dev backend listens on IPv4 only.
// Using the explicit IPv4 address sidesteps that whole class of "fetch failed" errors.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
const COOKIE_NAME = "williepb_token";

export function apiBase(): string {
  return API_BASE;
}

export function getToken(): string | undefined {
  try {
    return cookies().get(COOKIE_NAME)?.value;
  } catch {
    return undefined;
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body: unknown,
  ) {
    super(message);
  }
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  opts: { token?: string; cache?: RequestCache } = {},
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined),
  };
  const token = opts.token ?? getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers,
      cache: opts.cache ?? "no-store",
    });
  } catch (err) {
    throw new ApiError(networkErrorMessage(err), 0, null);
  }

  let body: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!res.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : res.statusText;
    throw new ApiError(detail, res.status, body);
  }
  return body as T;
}

export function networkErrorMessage(err: unknown): string {
  const msg = err instanceof Error ? err.message : String(err);
  // Surface the underlying cause Node.js attaches to fetch failures so users
  // see ECONNREFUSED / ENOTFOUND instead of an opaque "fetch failed".
  const cause = (err as { cause?: { code?: string; message?: string } } | null)?.cause;
  const code = cause?.code;
  if (code === "ECONNREFUSED") {
    return `백엔드(${API_BASE}) 연결이 거부됐습니다. 백엔드가 켜져 있는지 확인하세요. (ECONNREFUSED)`;
  }
  if (code === "ENOTFOUND") {
    return `백엔드 호스트를 찾을 수 없습니다 (${API_BASE}). NEXT_PUBLIC_API_BASE 값을 확인하세요. (ENOTFOUND)`;
  }
  if (code === "ETIMEDOUT") {
    return `백엔드(${API_BASE}) 응답 대기 중 시간 초과. (ETIMEDOUT)`;
  }
  return `${msg}${code ? ` (${code})` : ""} — 백엔드 주소: ${API_BASE}`;
}
