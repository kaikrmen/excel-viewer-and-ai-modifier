import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  if (pathname.startsWith("/api/")) {
    const origin = req.headers.get("origin");
    if (origin && !origin.startsWith(req.nextUrl.origin)) {
      return new NextResponse("Forbidden origin", { status: 403 });
    }
    if (!["GET", "POST"].includes(req.method)) {
      return new NextResponse("Method not allowed", { status: 405 });
    }
  }
  return NextResponse.next();
}
export const config = { matcher: ["/api/:path*"] };
