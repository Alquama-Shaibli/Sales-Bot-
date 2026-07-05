// App.jsx — Main application layout
import React from 'react';
import './index.css';
import ChatWidget from './components/ChatWidget';

export default function App() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

      {/* ── Top Header ──────────────────────────────────────────── */}
      <header style={{
        padding: '16px 32px',
        borderBottom: '1px solid rgba(255,255,255,0.07)',
        background: 'rgba(0,0,0,0.3)',
        backdropFilter: 'blur(20px)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        position: 'sticky', top: 0, zIndex: 100,
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '10px',
            background: 'linear-gradient(135deg, #4f8ef7, #7c3aed)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '18px', boxShadow: '0 4px 15px rgba(79,142,247,0.3)',
          }}>⚡</div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '1rem', letterSpacing: '-0.01em' }}>
              EnterpriseLead <span style={{ background: 'linear-gradient(90deg,#4f8ef7,#7c3aed)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>AI</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>B2B LEAD QUALIFICATION</div>
          </div>
        </div>

        {/* Stats Bar */}
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          {[
            { label: 'Avg Score', value: '78/100' },
            { label: 'Qualification', value: '2 min' },
            { label: 'Cost Reduction', value: '40%' },
          ].map(({ label, value }) => (
            <div key={label} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#93c5fd' }}>{value}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>{label.toUpperCase()}</div>
            </div>
          ))}
          <span style={{
            background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)',
            color: '#34d399', borderRadius: '99px', padding: '4px 12px',
            fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.03em',
          }}>● LIVE</span>
        </div>
      </header>

      {/* ── Main Layout ─────────────────────────────────────────── */}
      <main style={{ flex: 1, display: 'flex', gap: '0', overflow: 'hidden' }}>

        {/* Left sidebar — value props */}
        <aside style={{
          width: '240px', flexShrink: 0,
          borderRight: '1px solid rgba(255,255,255,0.06)',
          padding: '28px 20px',
          display: 'flex', flexDirection: 'column', gap: '20px',
          background: 'rgba(0,0,0,0.15)',
        }}
          className="hide-mobile"
        >
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.08em', marginBottom: '14px' }}>HOW IT WORKS</div>
            {[
              { step: '01', icon: '💬', title: 'Natural Chat', desc: 'AI asks qualifying questions conversationally' },
              { step: '02', icon: '⚡', title: 'Real-time Score', desc: '5-dimension analysis powered by Claude' },
              { step: '03', icon: '🔗', title: 'CRM Sync', desc: 'Auto-creates contact in HubSpot' },
              { step: '04', icon: '🔔', title: 'Sales Alert', desc: 'Instant SMS for hot leads (75+)' },
            ].map(({ step, icon, title, desc }) => (
              <div key={step} style={{ display: 'flex', gap: '12px', marginBottom: '18px' }}>
                <div style={{
                  width: '32px', height: '32px', borderRadius: '8px', flexShrink: 0,
                  background: 'rgba(79,142,247,0.1)', border: '1px solid rgba(79,142,247,0.2)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px',
                }}>{icon}</div>
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>{desc}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Score Legend */}
          <div style={{ marginTop: 'auto' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.08em', marginBottom: '10px' }}>SCORE LEGEND</div>
            {[
              { range: '75-100', label: 'Hot Lead', cls: 'badge-hot', icon: '🔴' },
              { range: '50-74', label: 'Warm Lead', cls: 'badge-warm', icon: '🟡' },
              { range: '0-49', label: 'Cold Lead', cls: 'badge-cold', icon: '🔵' },
            ].map(({ range, label, cls, icon }) => (
              <div key={range} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{icon} {range}</span>
                <span className={`badge ${cls}`} style={{ fontSize: '0.68rem' }}>{label}</span>
              </div>
            ))}
          </div>
        </aside>

        {/* Chat Area */}
        <div style={{ flex: 1, padding: '24px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <ChatWidget />
        </div>
      </main>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <footer style={{
        padding: '12px 32px',
        borderTop: '1px solid rgba(255,255,255,0.06)',
        background: 'rgba(0,0,0,0.2)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        fontSize: '0.72rem', color: 'var(--text-muted)',
      }}>
        <span>EnterpriseLead AI · FlowZint Hackathon 2026</span>
        <span>Powered by Claude claude-3-5-sonnet-20241022 · FastAPI · PostgreSQL</span>
      </footer>
    </div>
  );
}
