import React, { useMemo, useRef, useState, useEffect } from 'react'
import { chat, type ChatRequest, type ChatResponse, uploadFile, checkHealth } from './services/api'
import FileUpload from './components/FileUpload'

type Message = { role: 'user' | 'assistant'; content: string }

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [topK, setTopK] = useState(5)
  const [namespace, setNamespace] = useState('default')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [healthStatus, setHealthStatus] = useState<any>(null)
  const lastAnswerCitations = useRef<ChatResponse['citations']>([])

  const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading])

  // Check health status
  useEffect(() => {
    const checkHealthStatus = async () => {
      try {
        const health = await checkHealth()
        setHealthStatus(health)
      } catch (error) {
        console.log('Health check failed')
      }
    }
    checkHealthStatus()
  }, [])

  async function onSend() {
    if (!canSend) return
    const newMessages = [...messages, { role: 'user' as const, content: input }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)
    try {
      const req: ChatRequest = {
        message: input,
        history: newMessages.slice(-6),
        top_k: topK,
        namespace,
      }
      const res = await chat(req)
      lastAnswerCitations.current = res.citations
      setMessages([...newMessages, { role: 'assistant', content: res.answer }])
    } catch (e: any) {
      setMessages([...newMessages, { role: 'assistant', content: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  async function handleFileUpload(file: File, uploadNamespace: string) {
    try {
      const result = await uploadFile(file, uploadNamespace)
      return result
    } catch (error: any) {
      throw new Error(error.message)
    }
  }

  return (
    <div className="min-h-screen grid grid-cols-[260px_1fr] md:grid-cols-[320px_1fr]">
      {/* Sidebar */}
      <aside className={`border-r border-gray-200 dark:border-gray-800 p-4 hidden sm:block ${sidebarOpen ? '' : 'w-0 overflow-hidden'}`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold opacity-80">Workspace</h2>
          {healthStatus && (
            <div className="text-xs opacity-60">
              💻 Local Development
            </div>
          )}
        </div>
        
        
        <div className="space-y-4">
          <div>
            <label className="block text-xs mb-1 opacity-70">Namespace</label>
            <input
              type="text"
              className="w-full rounded border px-2 py-1 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700"
              value={namespace}
              onChange={(e) => setNamespace(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs mb-1 opacity-70">Top K</label>
            <input
              type="number"
              className="w-24 rounded border px-2 py-1 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700"
              value={topK}
              min={1}
              max={10}
              onChange={(e) => setTopK(parseInt(e.target.value || '5', 10))}
            />
          </div>
          <div>
            <h3 className="text-sm font-medium mb-2">Upload documents</h3>
            <FileUpload onUpload={handleFileUpload} namespace={namespace} />
          </div>
          {lastAnswerCitations.current.length > 0 && (
            <div className="text-sm">
              <div className="font-medium mb-1">Sources</div>
              <ul className="list-disc pl-5 space-y-1">
                {lastAnswerCitations.current.map((c) => (
                  <li key={c.id}>
                    <span className="opacity-70">{c.source}</span>
                    {typeof c.score === 'number' ? (
                      <span className="opacity-60"> — score {c.score.toFixed(3)}</span>
                    ) : null}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </aside>

      {/* Main chat area */}
      <div className="flex flex-col min-h-screen">
        <header className="px-4 py-3 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between sticky top-0 bg-inherit/80 backdrop-blur supports-[backdrop-filter]:bg-inherit/60">
          <div className="flex items-center gap-3">
            <button
              className="sm:hidden rounded border px-2 py-1 text-sm"
              onClick={() => setSidebarOpen((v) => !v)}
            >
              {sidebarOpen ? 'Hide' : 'Show'} Menu
            </button>
            <h1 className="text-base font-semibold">RAG Chatbot</h1>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-3xl px-4 py-6">
            {messages.length === 0 ? (
              <div className="text-center text-sm opacity-70 py-10">
                <p>Ask anything about your uploaded documents.</p>
              </div>
            ) : null}

            <div className="space-y-6">
              {messages.map((m, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className={`h-8 w-8 rounded-full flex items-center justify-center text-xs font-medium ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>
                    {m.role === 'user' ? 'U' : 'AI'}
                  </div>
                  <div className={`flex-1 whitespace-pre-wrap rounded-2xl px-4 py-3 ${m.role === 'user' ? 'bg-blue-50 dark:bg-blue-900/20' : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'}`}>
                    {m.content}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>

        <div className="sticky bottom-0 border-t border-gray-200 dark:border-gray-800 bg-gradient-to-t from-gray-100/80 to-gray-100/0 dark:from-gray-900/80 dark:to-gray-900/0">
          <div className="mx-auto w-full max-w-3xl px-4 py-3">
            <div className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-2 shadow-sm">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    onSend()
                  }
                }}
                rows={1}
                placeholder="Message AI..."
                className="w-full resize-none bg-transparent outline-none px-2 py-2"
              />
              <div className="flex items-center justify-between px-2 pb-1">
                <div className="text-[11px] opacity-60">Press Enter to send • Shift+Enter for new line</div>
                <button
                  onClick={onSend}
                  disabled={!canSend}
                  className="rounded bg-blue-600 text-white px-3 py-1.5 text-sm disabled:opacity-50"
                >
                  {loading ? 'Thinking…' : 'Send'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}