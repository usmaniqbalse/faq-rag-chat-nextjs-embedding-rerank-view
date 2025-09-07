import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  const backend = process.env.BACKEND_URL!;
  const apiKey = process.env.BACKEND_API_KEY!;
  const json = await req.json();

  const res = await fetch(`${backend}/v1/ask`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
    },
    body: JSON.stringify(json),
  });

  const body = await res.text();

  console.log("res", res);

  const init = {
    status: res.status,
    headers: {
      "content-type": res.headers.get("content-type") || "application/json",
    },
  };
  return new NextResponse(body, init);
}
