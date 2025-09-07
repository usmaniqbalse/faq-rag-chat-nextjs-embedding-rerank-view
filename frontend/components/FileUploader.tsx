"use client";

import { useState } from "react";

export default function FileUploader() {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setMsg(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("/api/ingest", { method: "POST", body: form });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail || "Upload failed");
      }
      const data = await res.json();
      setMsg(`✅ Ingested "${data.file_name}" with ${data.chunks} chunks`);
    } catch (err: any) {
      setMsg(`❌ ${err.message}`);
    } finally {
      setBusy(false);
      e.target.value = "";
      setTimeout(() => setMsg(null), 5000);
    }
  }

  return (
    <div className="flex items-center gap-3">
      <label className={`btn-ghost cursor-pointer ${busy ? "opacity-60" : ""}`}>
        <input
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={handleFile}
          disabled={busy}
        />
        📄 Upload PDF
      </label>
      {busy && <span className="text-sm muted">Processing…</span>}
      {msg && <span className="text-sm">{msg}</span>}
    </div>
  );
}
