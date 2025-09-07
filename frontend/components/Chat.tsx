"use client";

import { useEffect, useRef, useState } from "react";
import { Message, AskResponse } from "@/lib/types";
import { loadThread, saveThread, clearThread } from "@/lib/storage";
import MessageList from "./MessageList";
import Composer from "./Composer";
import FileUploader from "./FileUploader";

function uid() {
  return Math.random().toString(36).slice(2);
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages(loadThread());
  }, []);
  useEffect(() => {
    saveThread(messages);
  }, [messages]);
  useEffect(() => {
    listRef.current?.scrollTo({
      top: listRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, busy]);

  async function send(text: string) {
    const user: Message = {
      id: uid(),
      role: "user",
      content: text,
      createdAt: Date.now(),
    };
    setMessages((m) => [...m, user]);
    setBusy(true);
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question: text }),
      });
      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || `HTTP ${res.status}`);
      }
      const data = (await res.json()) as AskResponse & { retrieval?: any };

      const assistant: Message = {
        id: uid(),
        role: "assistant",
        content: data.answer || "No answer.",
        createdAt: Date.now(),
        meta: {
          retrieved: data.retrieved,
          reranked_ids: data.reranked_ids,
          retrieval_raw: (data as any).retrieval ?? undefined, // if backend later returns full Chroma result
        },
      };
      setMessages((m) => [...m, assistant]);
    } catch (e: any) {
      const assistant: Message = {
        id: uid(),
        role: "assistant",
        content: `Error: ${e?.message || "Failed to ask."}`,
        createdAt: Date.now(),
      };
      setMessages((m) => [...m, assistant]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-5xl flex-col px-4 py-6">
      <header className="card mb-4 flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 shadow"></div>
          <div>
            <div className="text-lg font-semibold">RAG Chat</div>
            <div className="text-xs muted">
              Ollama + ChromaDB + CrossEncoder
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <FileUploader />
          <button
            onClick={() => {
              clearThread();
              setMessages([]);
            }}
            className="btn-ghost"
            title="Clear local chat history"
          >
            Clear chat
          </button>
        </div>
      </header>

      <div ref={listRef} className="card flex-1 overflow-y-auto">
        <MessageList messages={messages} busy={busy} />
      </div>

      <footer className="mt-4 card">
        <Composer onSend={send} busy={busy} />
      </footer>
    </div>
  );
}
