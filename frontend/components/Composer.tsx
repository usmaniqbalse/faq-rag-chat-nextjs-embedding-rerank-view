"use client";
import { useState } from "react";

export default function Composer({
  onSend,
  busy,
}: {
  onSend: (text: string) => void;
  busy?: boolean;
}) {
  const [value, setValue] = useState("");

  return (
    <form
      className="flex items-end gap-3 p-4"
      onSubmit={(e) => {
        e.preventDefault();
        if (!value.trim() || busy) return;
        onSend(value.trim());
        setValue("");
      }}
    >
      <div className="flex-1">
        <textarea
          className="w-full resize-none rounded-2xl border border-slate-200 bg-white/70 p-3 outline-none ring-0 transition focus:border-blue-400 focus:ring-2 focus:ring-blue-200"
          rows={3}
          placeholder="Ask a question about your PDF..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={busy}
        />
        <div className="mt-1 text-xs muted">Shift+Enter for newline</div>
      </div>
      <button
        type="submit"
        className="btn-primary h-11 min-w-[88px]"
        disabled={busy || !value.trim()}
        aria-disabled={busy || !value.trim()}
        title="Send message"
      >
        {busy ? "Sending…" : "Send"}
      </button>
    </form>
  );
}
