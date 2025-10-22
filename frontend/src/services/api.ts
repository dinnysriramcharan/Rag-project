export type ChatRequest = {
  message: string
  history?: { role: 'user' | 'assistant'; content: string }[]
  top_k?: number
  namespace?: string
}

export type ChatResponse = {
  answer: string
  citations: { id: string; score?: number; source?: string }[]
}

// API base URL - use environment variable or default to localhost
export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// Debug: Log the actual API_BASE being used
console.log('API_BASE:', API_BASE)
console.log('VITE_API_BASE env:', import.meta.env.VITE_API_BASE)

export async function chat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.error || `Chat failed: ${res.status}`)
  }
  return res.json()
}

export async function uploadFile(file: File, namespace: string): Promise<any> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('namespace', namespace)

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData,
  })
  
  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.error || `Upload failed: ${res.status}`)
  }
  return res.json()
}

export async function checkHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/health`)
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status}`)
  }
  return res.json()
}