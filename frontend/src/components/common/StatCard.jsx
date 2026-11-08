import React from 'react';

export default function StatCard({ label, value, subtext, icon: Icon, accent = 'gold' }) {
  const accentColor = accent === 'sage' ? 'var(--accent-sage)' : 'var(--accent-gold)';
  const accentBg = accent === 'sage' ? 'var(--bg-sage-subtle)' : 'var(--bg-gold-subtle)';

  return (
    <div className="card" style={{
      position: 'relative',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
      }}>
        <span style={{
          fontSize: '0.78rem',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          color: 'var(--text-muted)',
        }}>
          {label}
        </span>
        {Icon && (
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: accentBg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: accentColor,
          }}>
            <Icon size={18} />
          </div>
        )}
      </div>

      <div>
        <div style={{
          fontFamily: 'var(--font-serif)',
          fontSize: '2.4rem',
          fontWeight: 600,
          color: 'var(--text-primary)',
          lineHeight: 1.1,
          marginBottom: '6px',
        }}>
          {value}
        </div>
        {subtext && (
          <div style={{
            fontSize: '0.82rem',
            color: 'var(--text-secondary)',
          }}>
            {subtext}
          </div>
        )}
      </div>
    </div>
  );
}

