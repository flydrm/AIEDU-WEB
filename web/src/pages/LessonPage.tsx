import React, { useEffect, useState } from 'react'

type Lesson = {
  date: string
  items: { type: 'card' | 'story' | 'family' | 'logic'; title: string; content: string }[]
}

export const LessonPage: React.FC = () => {
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      setLoading(true)
      setError(null)
      const resp = await fetch('/api/v1/lesson/today')
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data = await resp.json()
      setLesson(data)
    } catch (e: any) {
      setError(e?.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <main style={{ padding: 16 }}>
      <h2 style={{ fontSize: 18, marginBottom: 10 }}>今日微课</h2>
      {loading && <div>加载中...</div>}
      {error && <div style={{ color: '#c00' }}>{error}</div>}
      {lesson && (
        <div style={{ display: 'grid', gap: 8 }}>
          {lesson.items.map((it, idx) => (
            <div key={idx} style={{ border: '1px solid #eee', borderRadius: 8, padding: 8 }}>
              <div style={{ fontWeight: 'bold' }}>{it.title}</div>
              <div>{it.content}</div>
              <div style={{ fontSize: 12, color: '#888' }}>类型：{it.type}</div>
            </div>
          ))}
        </div>
      )}
      <div style={{ marginTop: 10 }}>
        <button onClick={load}>刷新</button>
      </div>
    </main>
  )
}

