export type Role = "user" | "assistant";

export interface AssistantMeta {
  retrieved?: string[][]; // documents
  reranked_ids?: number[]; // indices of selected chunks
  retrieval_raw?: any; // OPTIONAL: if backend returns the full Chroma result later
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  createdAt: number;
  meta?: AssistantMeta;
}

export interface AskResponse {
  answer: string;
  retrieved: string[][];
  reranked_ids: number[];
  // OPTIONAL backend extension:
  retrieval?: any;
}
