import React from 'react'

export const Sparkline: React.FC<{ data: number[]; width?: number; height?: number }> = ({ data, width = 240, height = 40 }) => {
  if (!data || data.length === 0) return null
  const max = Math.max(...data, 1)
  const pts = data.map((v, i) => {
    const x = (i / Math.max(1, data.length - 1)) * width
    const y = height - (v / max) * height
    return `${x},${y}`
  }).join(' ')
  return (
    <svg width={width} height={height} aria-label="sparkline" role="img">
      <polyline points={pts} fill="none" stroke="#2a7" strokeWidth={2} />
    </svg>
  )
}

