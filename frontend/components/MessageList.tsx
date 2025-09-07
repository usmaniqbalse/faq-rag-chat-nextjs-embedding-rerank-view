"use client";
import { Message } from "@/lib/types";
import JsonTree from "./JsonTree";

function formatTime(ts: number) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

export default function MessageList({
  messages,
  busy,
}: {
  messages: Message[];
  busy?: boolean;
}) {
  return (
    <div className="flex h-full flex-col space-y-4 p-4">
      {messages.length === 0 && (
        <div className="m-auto text-center">
          <div className="mx-auto mb-3 h-14 w-14 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-500 shadow-lg" />
          <p className="text-lg font-semibold">Ask about your PDF</p>
          <p className="muted">
            Upload a document, then type a question below.
          </p>
        </div>
      )}

      {messages.map((m) => {
        const isUser = m.role === "user";
        const retrieved = m.meta?.retrieved;
        const ids = m.meta?.reranked_ids ?? [];
        const raw = m.meta?.retrieval_raw; // if provided by backend

        // Fallback object for "retrieved documents" panel:
        // If you don't have the full raw Chroma result, show documents only.
        const retrievedPanelData = raw ?? { documents: retrieved ?? [] };

        return (
          <div
            key={m.id}
            className={`flex ${isUser ? "justify-end" : "justify-start"}`}
          >
            <div className="max-w-[80%]">
              <div className={isUser ? "bubble-user" : "bubble-assistant"}>
                <p className="whitespace-pre-wrap leading-relaxed">
                  {m.content}
                </p>
              </div>

              <div
                className={`mt-1 text-[11px] ${
                  isUser ? "text-right" : ""
                } muted`}
              >
                {formatTime(m.createdAt)}
              </div>

              {/* Streamlit-like expanders ONLY for assistant messages */}
              {!isUser && (retrieved || raw) && (
                <details className="mt-3">
                  <summary className="cursor-pointer select-none text-sm font-medium text-slate-600 hover:underline">
                    See retrieved documents
                  </summary>
                  <div className="mt-2 rounded-xl border bg-white p-2">
                    <JsonTree data={retrievedPanelData} />
                  </div>
                </details>
              )}

              {!isUser && ids && ids.length > 0 && (
                <details className="mt-2">
                  <summary className="cursor-pointer select-none text-sm font-medium text-slate-600 hover:underline">
                    See most relevant document ids
                  </summary>
                  <div className="mt-2 rounded-xl border bg-white p-2">
                    <JsonTree data={ids} />
                  </div>
                </details>
              )}
            </div>
          </div>
        );
      })}

      {busy && (
        <div className="flex justify-start">
          <div className="bubble-assistant">
            <span className="inline-flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-blue-500"></span>
              </span>
              Thinking…
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
