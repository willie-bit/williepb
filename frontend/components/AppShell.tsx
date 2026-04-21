import { logoutAction, requireUser } from "@/lib/auth";
import Sidebar from "./Sidebar";

export default async function AppShell({ children }: { children: React.ReactNode }) {
  const me = await requireUser();
  return (
    <div className="app">
      <Sidebar me={me} onLogout={logoutAction} />
      <main className="content">{children}</main>
    </div>
  );
}
