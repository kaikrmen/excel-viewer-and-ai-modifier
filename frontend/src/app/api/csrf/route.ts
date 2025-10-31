import { NextResponse } from "next/server";
import crypto from "node:crypto";

export async function GET() {
  return NextResponse.json({ csrf: crypto.randomBytes(16).toString("hex") });
}
