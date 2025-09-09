import React from 'react'

export const Bar: React.FC<{ data: number[]; width?: number; height?: number }> = ({ data, width = 240, height = 80 }) => {
  if (!data || data.length === 0) return null
  const max = Math.max(...data, 1)
  const barWidth = width / data.length
  return (
    <svg width={width} height={height} aria-label="bar-chart" role="img">
      {data.map((v, i) => {
        const h = (v / max) * height
        return <rect key={i} x={i * barWidth + 1} y={height - h} width={barWidth - 2} height={h} fill="#48a" />
      })}
    </svg>
  )
}

export const Heatmap: React.FC<{ data: number[]; cols?: number; size?: number; gap?: number }> = ({ data, cols = 7, size = 12, gap = 2 }) => {
  if (!data || data.length === 0) return null
  const rows = Math.ceil(data.length / cols)
  const w = cols * (size + gap)
  const h = rows * (size + gap)
  const color = (v: number) => {
    const t = Math.min(1, Math.max(0, v))
    const g = Math.round(255 * t)
    return `rgb(50, ${g}, 90)`
  }
  return (
    <svg width={w} height={h} aria-label="heatmap" role="img">
      {data.map((v, idx) => {
        const r = Math.floor(idx / cols)
        const c = idx % cols
        return <rect key={idx} x={c * (size + gap)} y={r * (size + gap)} width={size} height={size} rx={2} fill={color(v)} />
      })}
    </svg>
  )
}

