import { redirect } from "next/navigation";
import { fetchMe } from "@/lib/auth";

export default async function RootPage() {
  const me = await fetchMe();
  if (me) redirect("/dashboard");
  redirect("/login");
}
