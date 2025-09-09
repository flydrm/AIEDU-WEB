import React, { useEffect, useState } from 'react'
import { Sparkline } from './Sparkline'

export const ParentPage: React.FC = () => {
  const [tts, setTts] = useState(false)
  const [dark, setDark] = useState(false)
  const [metrics, setMetrics] = useState<string>('')
  const [summary, setSummary] = useState<{count: number; avg_success: number} | null>(null)
  const [detail, setDetail] = useState<Array<{concept_id: string; success_rate: number; last_days_ago: number}>>([])
  const [series, setSeries] = useState<Array<{date: string; success_rate: number; count: number}>>([])

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
      const d = await fetch('/api/v1/parent/mastery/detail')
      setDetail(await d.json())
      const s = await fetch('/api/v1/parent/mastery/timeseries?days=7')
      setSeries(await s.json())
    } catch (e) {
      setSummary({ count: 0, avg_success: 0 })
      setDetail([])
      setSeries([])
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
      {detail.length > 0 && (
        <div style={{ margin: '8px 0' }}>
          <div style={{ fontWeight: 'bold', marginBottom: 4 }}>明细</div>
          <ul>
            {detail.map((it) => (
              <li key={it.concept_id} style={{ fontSize: 13 }}>
                {it.concept_id}: {(it.success_rate * 100).toFixed(1)}%（{it.last_days_ago}天前）
              </li>
            ))}
          </ul>
        </div>
      )}
      {series.length > 0 && (
        <div style={{ margin: '8px 0' }}>
          <div style={{ fontWeight: 'bold', marginBottom: 4 }}>最近7天正确率</div>
          <Sparkline data={series.map(s => s.success_rate)} />
        </div>
      )}
      <pre aria-label="metrics" style={{ whiteSpace: 'pre-wrap', fontSize: 12, background: '#f8f8f8', padding: 8, borderRadius: 8 }}>
        {metrics}
      </pre>
    </main>
  )
}

