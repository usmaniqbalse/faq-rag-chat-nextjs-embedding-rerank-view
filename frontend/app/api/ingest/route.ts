import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  const backend = process.env.BACKEND_URL!;
  const apiKey = process.env.BACKEND_API_KEY!;

  const form = await req.formData();
  const res = await fetch(`${backend}/v1/ingest`, {
    method: "POST",
    body: form,
    headers: { "x-api-key": apiKey },
  });

  const body = await res.text();
  const init = {
    status: res.status,
    headers: {
      "content-type": res.headers.get("content-type") || "application/json",
    },
  };
  return new NextResponse(body, init);
}
