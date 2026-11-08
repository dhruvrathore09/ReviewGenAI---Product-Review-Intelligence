import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sparkles, BarChart3, Compass, Database, Activity, Menu, X, Home } from 'lucide-react';
import api from '../../services/api';

export default function Navbar() {
  const location = useLocation();
  const [health, setHealth] = useState({ status: 'checking', database: 'checking' });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    let isMounted = true;
    api.getHealth()
      .then((data) => {
        if (isMounted) setHealth(data);
      })
      .catch(() => {
        if (isMounted) setHealth({ status: 'offline', database: 'disconnected' });
      });
    return () => { isMounted = false; };
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  const navLinks = [
    { to: '/', label: 'Home', icon: Home },
    { to: '/products', label: 'Product Explorer', icon: Compass },
    { to: '/analytics', label: 'Review Analytics', icon: BarChart3 },
    { to: '/assistant', label: 'AI Assistant', icon: Sparkles },
  ];

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      backgroundColor: 'rgba(248, 246, 240, 0.95)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-light)',
      transition: 'all 0.2s ease',
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '70px',
      }}>
        {/* Brand Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <img
            src="/logo.png"
            alt="ReviewGenAI Logo"
            style={{
              width: '36px',
              height: '36px',
              objectFit: 'contain',
              display: 'block',
              filter: 'drop-shadow(0 2px 4px rgba(37, 40, 32, 0.12))',
            }}
          />
          <div>
            <div style={{
              fontFamily: 'var(--font-serif)',
              fontSize: '1.2rem',
              fontWeight: '600',
              letterSpacing: '0.03em',
              color: 'var(--text-primary)',
              lineHeight: 1.1,
            }}>
              ReviewGenAI
            </div>
            <div style={{
              fontSize: '0.65rem',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color: 'var(--text-muted)',
              fontWeight: 500,
            }}>
              Review Intelligence
            </div>
          </div>
        </Link>

        {/* Desktop Navigation Links (>= 768px) */}
        <nav className="desktop-nav" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '24px',
        }}>
          {navLinks.map((link) => {
            const Icon = link.icon;
            const active = isActive(link.to);
            return (
              <Link
                key={link.to}
                to={link.to}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.9rem',
                  fontWeight: active ? '600' : '500',
                  color: active ? 'var(--text-primary)' : 'var(--text-secondary)',
                  position: 'relative',
                  padding: '6px 0',
                  transition: 'color var(--transition-fast)',
                }}
              >
                <Icon size={15} color={active ? 'var(--accent-sage-dark)' : 'var(--accent-sage)'} />
                {link.label}
                {active && (
                  <span style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: '2px',
                    backgroundColor: 'var(--accent-gold)',
                    borderRadius: '1px',
                  }} />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right Section: Status Indicator & Mobile Menu Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Health Badge (compact on mobile) */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 12px',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.74rem',
          }}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: health.status === 'healthy' ? '#48BB78' : '#F56565',
              boxShadow: health.status === 'healthy' ? '0 0 6px #48BB78' : 'none',
            }} />
            <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
              {health.status === 'healthy' ? 'Active' : 'Connecting...'}
            </span>
          </div>

          {/* Mobile Hamburger Toggle Button (< 768px) */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="mobile-menu-btn"
            aria-label="Toggle navigation menu"
            style={{
              padding: '6px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-light)',
              backgroundColor: 'var(--bg-card)',
              color: 'var(--text-primary)',
              display: 'none',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
            }}
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Navigation (< 768px) */}
      {mobileMenuOpen && (
        <div className="mobile-nav-drawer" style={{
          backgroundColor: 'var(--bg-card)',
          borderBottom: '1px solid var(--border-light)',
          padding: '16px 20px 20px 20px',
          boxShadow: 'var(--shadow-md)',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
        }}>
          {navLinks.map((link) => {
            const Icon = link.icon;
            const active = isActive(link.to);
            return (
              <Link
                key={link.to}
                to={link.to}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.94rem',
                  fontWeight: active ? '600' : '500',
                  backgroundColor: active ? 'var(--bg-card-subtle)' : 'transparent',
                  color: active ? 'var(--text-primary)' : 'var(--text-secondary)',
                  border: active ? '1px solid var(--border-light)' : '1px solid transparent',
                  transition: 'background-color 0.15s ease',
                }}
              >
                <Icon size={18} color={active ? 'var(--accent-sage-dark)' : 'var(--text-muted)'} />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </div>
      )}

      {/* Responsive Inline CSS for Navbar */}
      <style>{`
        @media (max-width: 768px) {
          .desktop-nav {
            display: none !important;
          }
          .mobile-menu-btn {
            display: flex !important;
          }
        }
        @media (min-width: 769px) {
          .mobile-nav-drawer {
            display: none !important;
          }
        }
      `}</style>
    </header>
  );
}
