import React, { useRef, useState } from 'react'
import { ChatSSEClient, ChatChunk } from '../lib/sse'

type Msg = { role: 'user' | 'assistant'; content: string }

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('你好，给我讲个关于红色和勇敢的故事')
  const [loading, setLoading] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)
  const clientRef = useRef<ChatSSEClient | null>(null)

  const scrollToBottom = () => {
    const el = listRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }

  const send = async () => {
    if (loading) return
    setLoading(true)
    const next: Msg[] = [...messages, { role: 'user' as const, content: input }]
    setMessages(next)
    setInput('')

    const body = {
      model: 'gpt-5-chat',
      stream: true,
      messages: next.map((m: Msg) => ({ role: m.role, content: m.content })),
    }
    clientRef.current?.stop()
    const client = new ChatSSEClient('/api/v1/ai/chat')
    clientRef.current = client
    let acc = ''
    setMessages(prev => [...prev, { role: 'assistant', content: '' }])
    await client.start(body, (chunk: ChatChunk) => {
      if (chunk === '[DONE]') return
      if ((chunk as any).error) {
        acc += `\n[错误 ${ (chunk as any).error.status }: ${(chunk as any).error.message }]`
      } else if ((chunk as any).choices?.[0]?.delta?.content) {
        acc += (chunk as any).choices[0].delta.content
      } else if ((chunk as any).choices?.[0]?.message?.content) {
        acc += (chunk as any).choices[0].message.content
      }
      setMessages(prev => {
        const copy = [...prev]
        copy[copy.length - 1] = { role: 'assistant', content: acc }
        return copy
      })
      scrollToBottom()
    }, () => setLoading(false))
  }

  const stop = () => {
    clientRef.current?.stop()
    setLoading(false)
  }

  return (
    <main style={{ padding: 12, display: 'flex', flexDirection: 'column', height: 'calc(100dvh - 64px)' }}>
      <div ref={listRef} style={{ flex: 1, overflow: 'auto', border: '1px solid #eee', borderRadius: 8, padding: 8 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ margin: '6px 0' }}>
            <div style={{ fontWeight: 'bold', color: m.role === 'user' ? '#c00' : '#555' }}>{m.role === 'user' ? '我' : '小助手'}</div>
            <div>{m.content}</div>
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
        <input
          aria-label="输入消息"
          value={input}
          onChange={e => setInput(e.target.value)}
          style={{ flex: 1, height: 40, border: '1px solid #ccc', borderRadius: 8, padding: '0 10px' }}
        />
        <button onClick={send} disabled={loading} style={{ height: 40 }}>发送</button>
        <button onClick={stop} disabled={!loading} style={{ height: 40 }}>停止</button>
      </div>
    </main>
  )
}

