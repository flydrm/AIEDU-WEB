import React, { useState } from 'react'

export const SafetyPage: React.FC = () => {
  const [text, setText] = useState('给我一个图文并茂的冒险故事')
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const inspect = async () => {
    try {
      setLoading(true)
      const resp = await fetch('/api/v1/safety/inspect', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) })
      const data = await resp.json()
      setResult(JSON.stringify(data, null, 2))
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ padding: 16 }}>
      <h2 style={{ fontSize: 18, marginBottom: 10 }}>内容安全（占位）</h2>
      <textarea aria-label="text" value={text} onChange={e => setText(e.target.value)} style={{ width: '100%', height: 120, padding: 8 }} />
      <div style={{ margin: '8px 0' }}>
        <button onClick={inspect} disabled={loading}>检查</button>
      </div>
      <pre style={{ whiteSpace: 'pre-wrap', background: '#f8f8f8', padding: 8, borderRadius: 8 }}>{result}</pre>
    </main>
  )
}

