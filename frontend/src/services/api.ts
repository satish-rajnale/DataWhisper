/** API client for backend communication */
import axios from 'axios';
import type { ChatRequest, ChatResponse } from '../types';

// In production (Docker), use /api proxy through nginx
// In development, use the configured API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? '/api' : 'http://localhost:8000');

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/chat', request);
  return response.data;
}

