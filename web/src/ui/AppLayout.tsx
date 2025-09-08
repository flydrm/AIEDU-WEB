import React from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'

export const AppLayout: React.FC = () => {
  const location = useLocation()
  const active = (path: string) => (location.pathname === path ? 'font-bold' : '')
  return (
    <div style={{ minHeight: '100dvh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1, paddingBottom: 64 }}>
        <Outlet />
      </div>
      <nav
        aria-label="Bottom navigation"
        style={{
          position: 'fixed', bottom: 0, left: 0, right: 0,
          height: 64, display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)',
          borderTop: '1px solid #eee', background: '#fff'
        }}
      >
        <Link className={active('/')} to="/" style={itemStyle}>首页</Link>
        <Link className={active('/chat')} to="/chat" style={itemStyle}>聊天</Link>
        <Link className={active('/lesson')} to="/lesson" style={itemStyle}>微课</Link>
        <Link className={active('/safety')} to="/safety" style={itemStyle}>安全</Link>
        <Link className={active('/parent')} to="/parent" style={itemStyle}>家长</Link>
      </nav>
    </div>
  )
}

const itemStyle: React.CSSProperties = {
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  textDecoration: 'none', color: '#333', fontSize: 14
}

