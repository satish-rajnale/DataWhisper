/** TypeScript types for API communication */

export interface ChatRequest {
  query: string;
}

export interface ChatResponse {
  summary: string;
  rows: Record<string, unknown>[];
  explanation: string;
  sql: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sql?: string;
  rows?: Record<string, unknown>[];
  error?: string;
}

