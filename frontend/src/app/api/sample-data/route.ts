import { NextResponse } from "next/server";

export async function GET() {
  const base = process.env.BACKEND_URL!;
  const key = process.env.BACKEND_API_KEY!;
  const r = await fetch(`${base}/sample-data`, {
    headers: { "X-API-KEY": key },
    cache: "no-store",
  });
  const txt = await r.text();
  return new NextResponse(txt, {
    status: r.status,
    headers: {
      "Content-Type": r.headers.get("Content-Type") || "application/json",
    },
  });
}
