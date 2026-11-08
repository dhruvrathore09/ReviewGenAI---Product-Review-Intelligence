import React from 'react';
import { Link } from 'react-router-dom';
import { Database, ShieldCheck, Cpu } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{
      backgroundColor: 'var(--bg-card-subtle)',
      borderTop: '1px solid var(--border-light)',
      padding: '64px 0 32px 0',
      marginTop: '80px',
    }}>
      <div className="container">
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: '32px',
          marginBottom: '40px',
        }}>
          {/* Brand Col */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <img
                src="/logo.png"
                alt="ReviewGenAI Logo"
                style={{ width: '32px', height: '32px', objectFit: 'contain' }}
              />
              <div style={{
                fontFamily: 'var(--font-serif)',
                fontSize: '1.4rem',
                fontWeight: '600',
                color: 'var(--text-primary)',
              }}>
                ReviewGenAI
              </div>
            </div>
            <p style={{
              fontSize: '0.88rem',
              color: 'var(--text-secondary)',
              lineHeight: 1.6,
              marginBottom: '16px',
            }}>
              Transforming unstructured e-commerce feedback into evidence-grounded, verifiable product intelligence.
            </p>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-light)',
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
            }}>
              <Database size={13} color="var(--accent-sage)" />
              Amazon Reviews 2023 • Electronics
            </div>
          </div>

          {/* Navigation Links */}
          <div>
            <h4 style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '0.82rem',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              fontWeight: 600,
              color: 'var(--text-primary)',
              marginBottom: '16px',
            }}>
              Platform
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <li>
                <Link to="/" style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  Platform Overview
                </Link>
              </li>
              <li>
                <Link to="/products" style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  Product Explorer
                </Link>
              </li>
              <li>
                <Link to="/analytics" style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  Review Analytics
                </Link>
              </li>
              <li>
                <Link to="/assistant" style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  AI Review Assistant
                </Link>
              </li>
            </ul>
          </div>

          {/* Intelligence Architecture */}
          <div>
            <h4 style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '0.82rem',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              fontWeight: 600,
              color: 'var(--text-primary)',
              marginBottom: '16px',
            }}>
              Verified Pipeline
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                <ShieldCheck size={14} color="var(--accent-sage)" />
                Level 1–4 Data Ingestion & Cleaning
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                <Cpu size={14} color="var(--accent-sage)" />
                Level 5 ML Sentiment Classifiers
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--accent-gold)' }} />
                Level 7 RAG & Traceability (Architecture)
              </li>
            </ul>
          </div>
        </div>

        <div className="divider" style={{ margin: '0 0 24px 0' }} />

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
          fontSize: '0.8rem',
          color: 'var(--text-muted)',
        }}>
          <div>
            © 2026 Product Review Intelligence Platform. Built with React 19, Vite & FastAPI.
          </div>
          <div>
            PostgreSQL 16.6 • 5,027 Products • 7,991 Verified Reviews
          </div>
        </div>
      </div>
    </footer>
  );
}

