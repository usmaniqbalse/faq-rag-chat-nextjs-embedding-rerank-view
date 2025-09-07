const KEY = "rag-chat-thread-v1";

export function loadThread(): import("./types").Message[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveThread(messages: import("./types").Message[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY, JSON.stringify(messages));
}

export function clearThread() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(KEY);
}
