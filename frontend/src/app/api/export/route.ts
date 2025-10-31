import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const base = process.env.BACKEND_URL;
  const key = process.env.BACKEND_API_KEY;

  if (!base || !key) {
    return NextResponse.json(
      { error: "Missing BACKEND_URL or BACKEND_API_KEY in .env.local" },
      { status: 500 }
    );
  }

  const form = await req.formData(); // contiene "file" y "sheet_name"

  const upstream = await fetch(`${base}/export`, {
    method: "POST",
    headers: { "X-API-KEY": key },
    body: form, // pasa tal cual el multipart/form-data
    cache: "no-store",
  });

  // Devuelve el binario tal cual (xlsx)
  const buf = await upstream.arrayBuffer();
  const headers = new Headers(upstream.headers);
  // asegura content-type y filename
  headers.set(
    "Content-Type",
    headers.get("Content-Type") ??
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  );
  return new NextResponse(buf, { status: upstream.status, headers });
}
