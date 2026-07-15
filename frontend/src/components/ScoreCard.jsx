// components/ScoreCard.jsx — Elite 5-dimension lead score visualization
// Displays BANT-extended scores, AI reasoning, strengths/gaps, and strategic next step
import React, { useState } from 'react';
import { useScore } from '../hooks/useScore';

const DIMENSIONS = [
  { key: 'icp_fit',        label: 'ICP Fit',       weight: '30%', icon: '🏢', desc: 'Ideal Customer Profile match' },
  { key: 'intent_signals', label: 'Intent',         weight: '25%', icon: '🎯', desc: 'Urgency and pain severity' },
  { key: 'timeline',       label: 'Timeline',       weight: '20%', icon: '⏱️', desc: 'Buying decision horizon' },
  { key: 'authority',      label: 'Authority',      weight: '15%', icon: '👑', desc: 'Decision-making power' },
  { key: 'engagement',     label: 'Engagement',     weight: '10%', icon: '💬', desc: 'Conversation quality' },
];

function ScoreBar({ value, gradient, delay = 0 }) {
  return (
    <div className="score-bar-track">
      <div
        className="score-bar-fill"
        style={{
          background: gradient,
          width: `${value}%`,
          animationDelay: `${delay}s`,
          '--target-width': `${value}%`,
        }}
      />
    </div>
  );
}

function DimensionRow({ dimKey, label, weight, icon, desc, value, gradient, index, getScoreColor }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      key={dimKey}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'flex', flexDirection: 'column', gap: '6px',
        padding: '8px 10px', borderRadius: '8px',
        background: hovered ? 'rgba(255,255,255,0.04)' : 'transparent',
        transition: 'background 0.2s ease',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', gap: '5px', alignItems: 'center' }}>
          <span>{icon}</span> {label}
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>({weight})</span>
          {hovered && (
            <span style={{ fontSize: '0.67rem', color: 'var(--text-muted)', fontStyle: 'italic', marginLeft: '4px' }}>
              — {desc}
            </span>
          )}
        </span>
        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: getScoreColor(value), minWidth: '28px', textAlign: 'right' }}>
          {value}
        </span>
      </div>
      <ScoreBar value={value} gradient={gradient} delay={index * 0.1} />
    </div>
  );
}

export default function ScoreCard({ scoreData, conversationId, onQualify }) {
  const { getScoreColor, getScoreGradient, getScoreLabel, isQualifying, qualifyLead, qualifyResult } = useScore();
  const [showQualify, setShowQualify] = useState(false);
  const [leadEmail, setLeadEmail] = useState('');
  const [leadCompany, setLeadCompany] = useState('');

  if (!scoreData) return null;

  const { overall_score, breakdown, reasoning, key_strengths, key_gaps, next_step } = scoreData;
  const gradient = getScoreGradient(overall_score);
  const { label, badge, action } = getScoreLabel(overall_score);
  const isHot = overall_score >= 75;
  const isWarm = overall_score >= 50 && overall_score < 75;

  const handleQualify = async () => {
    const result = await qualifyLead(conversationId, {
      email: leadEmail,
      company: leadCompany,
    });
    if (result && onQualify) onQualify(result);
    setShowQualify(false);
  };

  // Recommendation display config
  const recConfig = {
    route_to_sales: { emoji: '🔴', text: 'Route to Sales', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.25)' },
    nurture:        { emoji: '🟡', text: 'Nurture Sequence', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.25)' },
    marketing_only: { emoji: '🔵', text: 'Marketing Only', bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.25)' },
  };
  const rec = recConfig[scoreData.recommendation] || recConfig.nurture;

  return (
    <div className="animate-slide-up" style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '14px' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f0f4ff' }}>Lead Score</h3>
        <span className={`badge ${badge}`}>{label}</span>
      </div>

      {/* Big Score Circle */}
      <div style={{ textAlign: 'center', padding: '16px 0' }}>
        <div style={{
          display: 'inline-flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          width: '130px', height: '130px', borderRadius: '50%',
          background: `conic-gradient(${getScoreColor(overall_score)} ${overall_score * 3.6}deg, rgba(255,255,255,0.06) 0deg)`,
          position: 'relative',
          boxShadow: isHot ? `0 0 40px ${getScoreColor(overall_score)}44` : 'none',
          animation: isHot ? 'glow-pulse 2s ease-in-out infinite' : 'none',
        }}>
          <div style={{
            position: 'absolute', inset: '8px', borderRadius: '50%',
            background: 'var(--bg-secondary)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          }}>
            <span style={{
              fontSize: '2.2rem', fontWeight: 800, lineHeight: 1,
              background: gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              animation: 'scoreCount 0.5s ease forwards',
            }}>
              {overall_score}
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 500 }}>/ 100</span>
          </div>
        </div>

        {/* Recommendation pill under circle */}
        <div style={{
          marginTop: '10px', display: 'inline-flex', alignItems: 'center', gap: '6px',
          padding: '4px 14px', borderRadius: '99px',
          background: rec.bg, border: `1px solid ${rec.border}`,
          fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)',
        }}>
          {rec.emoji} {rec.text}
        </div>
      </div>

      {/* Dimension Breakdown */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {DIMENSIONS.map(({ key, label, weight, icon, desc }, i) => {
          const val = breakdown?.[key] ?? 0;
          return (
            <DimensionRow
              key={key}
              dimKey={key}
              label={label}
              weight={weight}
              icon={icon}
              desc={desc}
              value={val}
              gradient={gradient}
              index={i}
              getScoreColor={getScoreColor}
            />
          );
        })}
      </div>

      {/* AI Reasoning */}
      {reasoning && (
        <div style={{
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: '10px', padding: '12px',
          fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.6,
        }}>
          <span style={{ color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
            💡 AI Analysis
          </span>
          {reasoning}
        </div>
      )}

      {/* Strengths & Gaps — Elite BANT fields */}
      {(key_strengths || key_gaps) && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {key_strengths && (
            <div style={{
              background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.2)',
              borderRadius: '8px', padding: '10px 12px',
            }}>
              <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#34d399', display: 'block', marginBottom: '3px' }}>
                ✅ Key Strengths
              </span>
              <span style={{ fontSize: '0.75rem', color: 'rgba(52,211,153,0.85)', lineHeight: 1.5 }}>
                {key_strengths}
              </span>
            </div>
          )}
          {key_gaps && (
            <div style={{
              background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.2)',
              borderRadius: '8px', padding: '10px 12px',
            }}>
              <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#fbbf24', display: 'block', marginBottom: '3px' }}>
                ⚠️ Areas to Develop
              </span>
              <span style={{ fontSize: '0.75rem', color: 'rgba(251,191,36,0.85)', lineHeight: 1.5 }}>
                {key_gaps}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Strategic Next Step */}
      {next_step && (
        <div style={{
          background: rec.bg, border: `1px solid ${rec.border}`,
          borderRadius: '8px', padding: '10px 12px',
        }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '3px' }}>
            📋 Recommended Next Step
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {next_step}
          </span>
        </div>
      )}

      {/* CTA Buttons */}
      {!qualifyResult && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: 'auto' }}>
          {!showQualify ? (
            <button className="btn-primary" onClick={() => setShowQualify(true)}
              style={{ width: '100%', padding: '12px' }}>
              {action} →
            </button>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <input
                className="chat-input" placeholder="Lead email (optional)"
                value={leadEmail} onChange={e => setLeadEmail(e.target.value)}
                style={{ fontSize: '0.85rem', padding: '10px 14px' }}
              />
              <input
                className="chat-input" placeholder="Company (optional)"
                value={leadCompany} onChange={e => setLeadCompany(e.target.value)}
                style={{ fontSize: '0.85rem', padding: '10px 14px' }}
              />
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn-ghost" onClick={() => setShowQualify(false)} style={{ flex: 1 }}>Cancel</button>
                <button className="btn-primary" onClick={handleQualify} disabled={isQualifying} style={{ flex: 2 }}>
                  {isQualifying ? 'Syncing...' : '✓ Confirm & Sync'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Qualify Success */}
      {qualifyResult && (
        <div style={{
          background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)',
          borderRadius: '10px', padding: '12px', textAlign: 'center',
          color: '#34d399', fontSize: '0.85rem', fontWeight: 600,
        }}>
          ✅ Lead synced to CRM! {qualifyResult.hubspot_contact_id ? '→ HubSpot' : '→ DB'} <br/>
          <span style={{ fontSize: '0.75rem', fontWeight: 400, color: 'rgba(52,211,153,0.7)' }}>{qualifyResult.message}</span>
        </div>
      )}
    </div>
  );
}
