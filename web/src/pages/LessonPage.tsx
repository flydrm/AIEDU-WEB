import React, { useEffect, useState } from 'react'

export const LessonPage: React.FC = () => {
  const [plan, setPlan] = useState<any | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      setLoading(true)
      setError(null)
      const resp = await fetch('/api/v1/lesson/today')
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data = await resp.json()
      setPlan(data)
    } catch (e: any) {
      setError(e?.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const start = async (conceptId: string) => {
    await fetch(`/api/v1/lesson/event/start?concept_id=${encodeURIComponent(conceptId)}`, { method: 'POST' })
  }
  const help = async (conceptId: string) => {
    await fetch(`/api/v1/lesson/event/help?concept_id=${encodeURIComponent(conceptId)}`, { method: 'POST' })
  }
  const complete = async (conceptId: string, success: boolean) => {
    await fetch(`/api/v1/lesson/event?concept_id=${encodeURIComponent(conceptId)}&success=${success ? 'true' : 'false'}`, { method: 'POST' })
  }

  useEffect(() => { load() }, [])

  const renderItem = (it: any) => {
    const cid = it.id || it.title || `${it.type}-${it.content?.slice(0, 6)}`
    return (
      <div key={cid} style={{ border: '1px solid #eee', borderRadius: 8, padding: 8 }}>
        <div style={{ fontWeight: 'bold' }}>{it.title || it.id || it.type}</div>
        <div>{it.content || it.lines?.join('、') || ''}</div>
        <div style={{ fontSize: 12, color: '#888' }}>类型：{it.type || 'card'}</div>
        <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
          <button onClick={() => start(cid)}>开始</button>
          <button onClick={() => help(cid)}>需要帮助</button>
          <button onClick={() => complete(cid, true)}>完成(正确)</button>
          <button onClick={() => complete(cid, false)}>完成(需巩固)</button>
        </div>
      </div>
    )
  }

  return (
    <main style={{ padding: 16 }}>
      <h2 style={{ fontSize: 18, marginBottom: 10 }}>今日微课</h2>
      {loading && <div>加载中...</div>}
      {error && <div style={{ color: '#c00' }}>{error}</div>}
      {plan && (
        <div style={{ display: 'grid', gap: 8 }}>
          {plan.cards?.map((it: any) => renderItem({ ...it, type: 'card', content: (it.lines||[]).join('、') }))}
          {plan.story?.map((it: any) => renderItem({ ...it, type: 'story', content: it.prompt }))}
          {plan.family?.map((it: any) => renderItem({ ...it, type: 'family', content: (it.lines||[]).join('、') }))}
          {plan.logic?.map((it: any) => renderItem({ ...it, type: 'logic', content: (it.lines||[]).join('、') }))}
        </div>
      )}
      <div style={{ marginTop: 10 }}>
        <button onClick={load}>刷新</button>
      </div>
    </main>
  )
}

