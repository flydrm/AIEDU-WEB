import React, { useEffect, useState } from 'react'

export const ParentPage: React.FC = () => {
  const [tts, setTts] = useState(false)
  const [dark, setDark] = useState(false)
  const [metrics, setMetrics] = useState<string>('')
  const [summary, setSummary] = useState<{count: number; avg_success: number} | null>(null)

  useEffect(() => {
    document.documentElement.style.background = dark ? '#111' : '#fff'
    document.body.style.color = dark ? '#eee' : '#222'
  }, [dark])

  const loadMetrics = async () => {
    try {
      const resp = await fetch('/metrics')
      const text = await resp.text()
      setMetrics(text)
    } catch (e) {
      setMetrics('# metrics 加载失败')
    }
  }

  const loadMastery = async () => {
    try {
      const resp = await fetch('/api/v1/parent/mastery')
      const js = await resp.json()
      setSummary(js)
    } catch (e) {
      setSummary({ count: 0, avg_success: 0 })
    }
  }

  return (
    <main style={{ padding: 16 }}>
      <h2 style={{ fontSize: 18, marginBottom: 12 }}>家长中心</h2>
      <div style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
        <label>
          <input type="checkbox" checked={tts} onChange={e => setTts(e.target.checked)} /> 启用 TTS（占位）
        </label>
        <label>
          <input type="checkbox" checked={dark} onChange={e => setDark(e.target.checked)} /> 夜间模式
        </label>
      </div>
      <div style={{ marginBottom: 8 }}>
        <button onClick={loadMetrics}>查看服务指标</button>
        <button onClick={loadMastery} style={{ marginLeft: 8 }}>掌握度汇总</button>
      </div>
      {summary && (
        <div style={{ marginBottom: 8 }}>
          <strong>掌握度</strong>: 条目 {summary.count}，平均正确率 {(summary.avg_success * 100).toFixed(1)}%
        </div>
      )}
      <pre aria-label="metrics" style={{ whiteSpace: 'pre-wrap', fontSize: 12, background: '#f8f8f8', padding: 8, borderRadius: 8 }}>
        {metrics}
      </pre>
    </main>
  )
}

