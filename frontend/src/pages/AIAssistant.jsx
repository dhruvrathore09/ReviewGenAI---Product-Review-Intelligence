import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, Send, User, RotateCcw, Copy, Check, 
  ThumbsUp, ThumbsDown, Trash2, ArrowUpRight, ChevronRight, 
  Plus, MessageSquare, ShieldCheck, Zap, X, Menu
} from 'lucide-react';
import api from '../services/api';

const STARTER_PROMPTS = [
  {
    icon: "⚖️",
    label: "Compare Models",
    text: "Compare Apple iPhone 8 Plus vs Samsung Galaxy S20 FE"
  },
  {
    icon: "⚠️",
    label: "Failure Modes",
    text: "What are the common failure modes and flaws of Apple MacBook Air?"
  },
  {
    icon: "🌟",
    label: "Recommendations",
    text: "Recommend the best everyday laptop under $500"
  },
  {
    icon: "🎧",
    label: "Battery Lifespan",
    text: "Which wireless earbuds have the best battery lifespan?"
  }
];

export default function AIAssistant() {
  const [sessions, setSessions] = useState(() => {
    try {
      const saved = localStorage.getItem('reviewgenai_chat_sessions_v3');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {
      // ignore
    }
    return [{ id: 'session_init', title: 'New Conversation', messages: [], createdAt: Date.now() }];
  });

  const [activeSessionId, setActiveSessionId] = useState(() => {
    try {
      const saved = localStorage.getItem('reviewgenai_chat_sessions_v3');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed[0].id;
      }
    } catch {
      // ignore
    }
    return 'session_init';
  });

  const [inputText, setInputText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [feedbackState, setFeedbackState] = useState({});
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const scrollContainerRef = useRef(null);

  // Active session object
  const currentSession = sessions.find(s => s.id === activeSessionId) || sessions[0] || { id: 'default', title: 'New Conversation', messages: [] };
  const messages = currentSession.messages || [];

  // Persist sessions
  useEffect(() => {
    try {
      localStorage.setItem('reviewgenai_chat_sessions_v3', JSON.stringify(sessions));
    } catch (e) {
      console.warn("Could not save chat sessions:", e);
    }
  }, [sessions]);

  // Focus input and scroll to bottom on mount
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
    textareaRef.current?.focus();
  }, [activeSessionId]);

  // Auto-scroll when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isGenerating]);

  // Create a new chat session
  const handleNewChat = () => {
    const newId = `session_${Date.now()}`;
    const newSession = {
      id: newId,
      title: 'New Conversation',
      messages: [],
      createdAt: Date.now()
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newId);
    setInputText('');
    setMobileSidebarOpen(false);
    setTimeout(() => textareaRef.current?.focus(), 50);
  };

  // Delete a chat session
  const handleDeleteSession = (e, id) => {
    e.stopPropagation();
    if (sessions.length <= 1) {
      const resetSession = { id: `session_${Date.now()}`, title: 'New Conversation', messages: [], createdAt: Date.now() };
      setSessions([resetSession]);
      setActiveSessionId(resetSession.id);
      return;
    }
    const filtered = sessions.filter(s => s.id !== id);
    setSessions(filtered);
    if (activeSessionId === id) {
      setActiveSessionId(filtered[0].id);
    }
  };

  // Clear current conversation messages
  const handleClearCurrentChat = () => {
    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        return { ...s, title: 'New Conversation', messages: [] };
      }
      return s;
    }));
    setInputText('');
    textareaRef.current?.focus();
  };

  // Auto-resize textarea
  const handleTextareaChange = (e) => {
    setInputText(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 110)}px`;
    }
  };

  // Send message
  const handleSendMessage = async (textToSend = null) => {
    const query = (textToSend || inputText).trim();
    if (!query || isGenerating) return;

    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = '42px';
    }

    const userMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const updatedMessages = [...messages, userMessage];
    const newTitle = messages.length === 0 ? (query.length > 28 ? query.substring(0, 28) + '...' : query) : currentSession.title;

    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        return {
          ...s,
          title: newTitle,
          messages: updatedMessages
        };
      }
      return s;
    }));

    setIsGenerating(true);

    try {
      const response = await api.chatWithAssistant(
        updatedMessages.map(m => ({ role: m.role, content: m.content })),
        query
      );

      const assistantMessage = {
        role: 'assistant',
        content: response.reply,
        products: response.products || [],
        suggestedFollowups: response.suggested_followups || [],
        sources: response.sources || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setSessions(prev => prev.map(s => {
        if (s.id === activeSessionId) {
          return {
            ...s,
            messages: [...updatedMessages, assistantMessage]
          };
        }
        return s;
      }));
    } catch (err) {
      console.error("Assistant chat error:", err);
      const errorMessage = {
        role: 'assistant',
        content: "⚠️ **Service Notice**: Could not connect to the Review Intelligence API. Please make sure the backend server is running on `http://127.0.0.1:8000`.",
        products: [],
        suggestedFollowups: ["Try asking again", "Recommend a laptop under $500"],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setSessions(prev => prev.map(s => {
        if (s.id === activeSessionId) {
          return {
            ...s,
            messages: [...updatedMessages, errorMessage]
          };
        }
        return s;
      }));
    } finally {
      setIsGenerating(false);
      setTimeout(() => textareaRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Copy reply
  const handleCopy = (content, index) => {
    navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Feedback
  const handleFeedback = (index, type) => {
    setFeedbackState(prev => ({
      ...prev,
      [index]: prev[index] === type ? null : type
    }));
  };

  // Markdown rendering
  const renderMarkdown = (text) => {
    if (!text) return null;
    const lines = text.split('\n');
    const elements = [];
    let tableBuffer = [];
    let inTable = false;

    const flushTable = (key) => {
      if (tableBuffer.length > 0) {
        const headerLine = tableBuffer[0];
        const bodyLines = tableBuffer.slice(2);
        const headers = headerLine.split('|').map(c => c.trim()).filter(Boolean);

        elements.push(
          <div key={`table-${key}`} style={{ overflowX: 'auto', margin: '14px 0', WebkitOverflowScrolling: 'touch' }}>
            <table style={{
              width: '100%',
              minWidth: '320px',
              borderCollapse: 'collapse',
              fontSize: '0.84rem',
              backgroundColor: 'var(--bg-primary)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-light)'
            }}>
              <thead>
                <tr style={{ backgroundColor: 'var(--bg-card-subtle)', borderBottom: '2px solid var(--border-light)' }}>
                  {headers.map((h, i) => (
                    <th key={i} style={{ padding: '8px 10px', textAlign: 'left', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {bodyLines.map((row, rIdx) => {
                  const cells = row.split('|').map(c => c.trim()).filter(Boolean);
                  return (
                    <tr key={rIdx} style={{ borderBottom: '1px solid var(--border-light)' }}>
                      {cells.map((cell, cIdx) => (
                        <td key={cIdx} style={{ padding: '7px 10px', color: 'var(--text-secondary)' }}>
                          {formatInlineMarkdown(cell)}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        );
        tableBuffer = [];
        inTable = false;
      }
    };

    lines.forEach((line, idx) => {
      const trimmed = line.trim();

      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        inTable = true;
        tableBuffer.push(trimmed);
        return;
      } else if (inTable) {
        flushTable(idx);
      }

      if (trimmed.startsWith('## ')) {
        elements.push(
          <h2 key={idx} style={{ fontSize: 'clamp(1.1rem, 2.5vw, 1.25rem)', fontWeight: 700, margin: '14px 0 6px 0', color: 'var(--text-primary)' }}>
            {formatInlineMarkdown(trimmed.replace(/^##\s+/, ''))}
          </h2>
        );
      } else if (trimmed.startsWith('### ')) {
        elements.push(
          <h3 key={idx} style={{ fontSize: 'clamp(0.95rem, 2vw, 1.05rem)', fontWeight: 600, margin: '10px 0 4px 0', color: 'var(--text-primary)' }}>
            {formatInlineMarkdown(trimmed.replace(/^###\s+/, ''))}
          </h3>
        );
      } else if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
        elements.push(
          <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', margin: '3px 0', paddingLeft: '2px' }}>
            <span style={{ color: 'var(--accent-sage)', fontWeight: 'bold' }}>•</span>
            <div style={{ flex: 1, fontSize: '0.88rem', lineHeight: 1.5 }}>
              {formatInlineMarkdown(trimmed.replace(/^[\*\-]\s+/, ''))}
            </div>
          </div>
        );
      } else if (trimmed.startsWith('> ')) {
        elements.push(
          <blockquote key={idx} style={{
            margin: '8px 0',
            padding: '8px 12px',
            borderLeft: '3px solid var(--accent-terracotta)',
            backgroundColor: 'var(--bg-primary)',
            borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
            fontStyle: 'italic',
            fontSize: '0.84rem',
            color: 'var(--text-secondary)',
            lineHeight: 1.45
          }}>
            {formatInlineMarkdown(trimmed.replace(/^>\s+/, ''))}
          </blockquote>
        );
      } else if (trimmed.length > 0) {
        elements.push(
          <p key={idx} style={{ margin: '5px 0', fontSize: '0.88rem', lineHeight: 1.5, color: 'var(--text-secondary)' }}>
            {formatInlineMarkdown(trimmed)}
          </p>
        );
      }
    });

    if (inTable) flushTable('end');
    return elements;
  };

  const formatInlineMarkdown = (text) => {
    if (!text) return '';
    const parts = [];
    const regex = /(\*\*.*?\*\*|\*.*?\*|`.*?`)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }
      const token = match[0];
      if (token.startsWith('**') && token.endsWith('**')) {
        parts.push(<strong key={match.index} style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{token.slice(2, -2)}</strong>);
      } else if (token.startsWith('*') && token.endsWith('*')) {
        parts.push(<em key={match.index}>{token.slice(1, -1)}</em>);
      } else if (token.startsWith('`') && token.endsWith('`')) {
        parts.push(
          <code key={match.index} style={{
            padding: '2px 5px',
            backgroundColor: 'var(--bg-card-subtle)',
            borderRadius: '4px',
            fontSize: '0.78rem',
            fontFamily: 'monospace'
          }}>
            {token.slice(1, -1)}
          </code>
        );
      }
      lastIndex = regex.lastIndex;
    }
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }
    return parts.length > 0 ? parts : text;
  };

  return (
    <div style={{
      display: 'flex',
      height: '100%',
      width: '100%',
      backgroundColor: 'var(--bg-primary)',
      overflow: 'hidden',
      position: 'relative',
    }}>
      {/* MOBILE BACKDROP FOR SIDEBAR (< 768px) */}
      {mobileSidebarOpen && (
        <div
          onClick={() => setMobileSidebarOpen(false)}
          className="assistant-mobile-backdrop"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.45)',
            zIndex: 80,
          }}
        />
      )}

      {/* LEFT SIDEBAR: Chat History (Docked on Desktop, Drawer on Mobile) */}
      <div className={`assistant-sidebar ${mobileSidebarOpen ? 'open' : ''}`} style={{
        width: '260px',
        height: '100%',
        backgroundColor: 'var(--bg-card)',
        borderRight: '1px solid var(--border-light)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
        zIndex: 90,
        transition: 'transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
      }}>
        {/* Sidebar Header with Close button on mobile */}
        <div style={{
          padding: '12px 14px 10px 14px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <button
            onClick={handleNewChat}
            className="btn btn-primary"
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              padding: '8px 12px',
              fontSize: '0.84rem',
              fontWeight: 600,
              borderRadius: 'var(--radius-sm)'
            }}
          >
            <Plus size={15} />
            New Chat
          </button>

          <button
            onClick={() => setMobileSidebarOpen(false)}
            className="assistant-sidebar-close"
            style={{
              background: 'none',
              border: '1px solid var(--border-light)',
              borderRadius: 'var(--radius-sm)',
              padding: '6px',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              display: 'none',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Chat History List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '0 8px 12px 8px'
        }}>
          <div style={{
            fontSize: '0.68rem',
            textTransform: 'uppercase',
            color: 'var(--text-muted)',
            fontWeight: 600,
            padding: '6px 8px 4px 8px'
          }}>
            Chat History
          </div>

          {sessions.map(s => {
            const isActive = s.id === activeSessionId;
            return (
              <div
                key={s.id}
                onClick={() => {
                  setActiveSessionId(s.id);
                  setMobileSidebarOpen(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 10px',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  backgroundColor: isActive ? 'var(--bg-card-subtle)' : 'transparent',
                  border: isActive ? '1px solid var(--border-light)' : '1px solid transparent',
                  marginBottom: '3px',
                  transition: 'background-color 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                  <MessageSquare size={13} color={isActive ? 'var(--accent-sage-dark)' : 'var(--text-muted)'} />
                  <span style={{
                    fontSize: '0.8rem',
                    color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                    fontWeight: isActive ? 600 : 400,
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    maxWidth: '150px'
                  }}>
                    {s.title}
                  </span>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(e, s.id)}
                  title="Delete chat"
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    padding: '2px',
                    display: 'flex',
                    alignItems: 'center',
                    opacity: isActive ? 0.8 : 0.3
                  }}
                >
                  <Trash2 size={12} />
                </button>
              </div>
            );
          })}
        </div>

        {/* Sidebar Footer (Grounding Info) */}
        <div style={{
          padding: '10px 14px',
          borderTop: '1px solid var(--border-light)',
          backgroundColor: 'var(--bg-card-subtle)',
          fontSize: '0.7rem',
          color: 'var(--text-muted)',
          lineHeight: 1.4
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 600, color: 'var(--accent-sage-dark)', marginBottom: '2px' }}>
            <ShieldCheck size={12} />
            PostgreSQL Grounded
          </div>
          <div>8,866 Products • 9,733 Reviews</div>
        </div>
      </div>

      {/* RIGHT MAIN CHAT AREA (Fits screen exactly) */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
        position: 'relative'
      }}>
        {/* Top Header Bar */}
        <div style={{
          height: '46px',
          padding: '0 16px',
          backgroundColor: 'var(--bg-card)',
          borderBottom: '1px solid var(--border-light)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexShrink: 0
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {/* Mobile History Toggle Button */}
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="assistant-mobile-toggle"
              style={{
                display: 'none',
                alignItems: 'center',
                gap: '5px',
                padding: '4px 8px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-light)',
                backgroundColor: 'var(--bg-primary)',
                fontSize: '0.74rem',
                color: 'var(--text-secondary)',
                cursor: 'pointer'
              }}
            >
              <MessageSquare size={13} />
              <span>History</span>
            </button>

            <span style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-primary)' }}>
              AI Review Assistant
            </span>
            <span className="badge badge-sage" style={{ fontSize: '0.64rem', padding: '1px 6px' }}>
              <Zap size={9} /> Online
            </span>
          </div>

          {messages.length > 0 && (
            <button
              onClick={handleClearCurrentChat}
              className="btn btn-outline"
              style={{ fontSize: '0.74rem', padding: '4px 8px', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <RotateCcw size={11} />
              Clear
            </button>
          )}
        </div>

        {/* Messages Scroll Area */}
        <div
          ref={scrollContainerRef}
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '16px 16px 12px 16px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: messages.length === 0 ? 'center' : 'flex-start'
          }}
        >
          <div style={{ maxWidth: '780px', width: '100%', margin: '0 auto' }}>
            {/* Empty Chat Welcome Hero */}
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '8px 0' }}>
                <div style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '12px',
                  backgroundColor: 'var(--accent-sage-dark)',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 10px auto',
                  boxShadow: '0 4px 14px rgba(45, 106, 79, 0.2)'
                }}>
                  <Sparkles size={20} />
                </div>
                <h2 style={{ fontSize: 'clamp(1.2rem, 3vw, 1.45rem)', color: 'var(--text-primary)', marginBottom: '4px' }}>
                  What product can I analyze for you?
                </h2>
                <p style={{ fontSize: 'clamp(0.8rem, 2vw, 0.88rem)', color: 'var(--text-secondary)', maxWidth: '460px', margin: '0 auto 16px auto', lineHeight: 1.45 }}>
                  Ask questions to evaluate debiased ratings, real buyer failure modes, and head-to-head comparisons.
                </p>

                {/* Responsive Starter Prompts Grid */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '8px',
                  textAlign: 'left'
                }}>
                  {STARTER_PROMPTS.map((p, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleSendMessage(p.text)}
                      style={{
                        padding: '10px 12px',
                        backgroundColor: 'var(--bg-card)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--border-light)',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = 'var(--accent-sage)';
                        e.currentTarget.style.backgroundColor = 'var(--bg-card-subtle)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border-light)';
                        e.currentTarget.style.backgroundColor = 'var(--bg-card)';
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.74rem', color: 'var(--accent-sage-dark)', fontWeight: 600, marginBottom: '2px' }}>
                        <span>{p.icon}</span>
                        <span>{p.label}</span>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-primary)', lineHeight: 1.3 }}>
                        {p.text}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              /* Message Flow */
              messages.map((msg, idx) => {
                const isUser = msg.role === 'user';
                return (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      gap: '10px',
                      marginBottom: '16px',
                      alignItems: 'flex-start',
                      justifyContent: isUser ? 'flex-end' : 'flex-start'
                    }}
                  >
                    {!isUser && (
                      <div style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        backgroundColor: 'var(--accent-sage-dark)',
                        color: '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        marginTop: '2px'
                      }}>
                        <Sparkles size={14} />
                      </div>
                    )}

                    <div style={{ maxWidth: isUser ? '90%' : '100%', minWidth: 0 }}>
                      <div style={{
                        backgroundColor: isUser ? 'var(--text-primary)' : 'var(--bg-card)',
                        color: isUser ? '#fff' : 'inherit',
                        padding: '11px 14px',
                        borderRadius: 'var(--radius-sm)',
                        border: isUser ? 'none' : '1px solid var(--border-light)',
                        boxShadow: isUser ? 'none' : 'var(--shadow-sm)'
                      }}>
                        {isUser ? (
                          <div style={{ fontSize: '0.88rem', lineHeight: 1.5 }}>
                            {msg.content}
                          </div>
                        ) : (
                          renderMarkdown(msg.content)
                        )}

                        {/* Interactive Product Cards */}
                        {!isUser && msg.products && msg.products.length > 0 && (
                          <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--border-light)' }}>
                            <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '6px' }}>
                              Referenced Products ({msg.products.length})
                            </div>
                            <div style={{
                              display: 'grid',
                              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                              gap: '8px'
                            }}>
                              {msg.products.map(prod => (
                                <div
                                  key={prod.product_id}
                                  style={{
                                    backgroundColor: 'var(--bg-primary)',
                                    borderRadius: 'var(--radius-sm)',
                                    border: '1px solid var(--border-light)',
                                    padding: '9px 11px',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    justifyContent: 'space-between'
                                  }}
                                >
                                  <div>
                                    <div style={{ fontSize: '0.66rem', color: 'var(--accent-sage-dark)', fontWeight: 600, textTransform: 'uppercase' }}>
                                      {prod.brand || 'Electronics'}
                                    </div>
                                    <div style={{
                                      fontSize: '0.8rem',
                                      fontWeight: 600,
                                      color: 'var(--text-primary)',
                                      lineHeight: 1.25,
                                      margin: '2px 0 4px 0',
                                      display: '-webkit-box',
                                      WebkitLineClamp: 2,
                                      WebkitBoxOrient: 'vertical',
                                      overflow: 'hidden'
                                    }}>
                                      {prod.product_name}
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', margin: '3px 0', flexWrap: 'wrap' }}>
                                      <span style={{
                                        fontSize: '0.72rem',
                                        fontWeight: 700,
                                        color: 'var(--accent-sage-dark)',
                                        backgroundColor: 'var(--bg-card-subtle)',
                                        padding: '1px 5px',
                                        borderRadius: '4px',
                                        border: '1px solid var(--border-light)'
                                      }}>
                                        {prod.honest_rating}★
                                      </span>
                                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                        Grade {prod.quality_grade}
                                      </span>
                                      <span style={{ fontSize: '0.7rem', color: 'var(--accent-terracotta)', fontWeight: 600 }}>
                                        {prod.critical_complaint_rate}% Defects
                                      </span>
                                    </div>
                                  </div>

                                  <Link
                                    to={`/products/${prod.product_id}`}
                                    className="btn btn-outline"
                                    style={{
                                      marginTop: '6px',
                                      padding: '4px 6px',
                                      fontSize: '0.7rem',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      gap: '3px'
                                    }}
                                  >
                                    View Intelligence <ArrowUpRight size={10} />
                                  </Link>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Action Bar */}
                      {!isUser && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '3px', paddingLeft: '4px' }}>
                          <button
                            onClick={() => handleCopy(msg.content, idx)}
                            title="Copy message"
                            style={{
                              background: 'none',
                              border: 'none',
                              color: 'var(--text-muted)',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '3px',
                              fontSize: '0.7rem'
                            }}
                          >
                            {copiedIndex === idx ? <Check size={11} color="var(--accent-sage)" /> : <Copy size={11} />}
                            {copiedIndex === idx ? 'Copied' : 'Copy'}
                          </button>

                          <button
                            onClick={() => handleFeedback(idx, 'up')}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: feedbackState[idx] === 'up' ? 'var(--accent-sage-dark)' : 'var(--text-muted)',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center'
                            }}
                          >
                            <ThumbsUp size={11} />
                          </button>

                          <button
                            onClick={() => handleFeedback(idx, 'down')}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: feedbackState[idx] === 'down' ? 'var(--accent-terracotta)' : 'var(--text-muted)',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center'
                            }}
                          >
                            <ThumbsDown size={11} />
                          </button>
                        </div>
                      )}

                      {/* Suggested Follow-Ups */}
                      {!isUser && msg.suggestedFollowups && msg.suggestedFollowups.length > 0 && idx === messages.length - 1 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginTop: '8px' }}>
                          {msg.suggestedFollowups.map((chip, cIdx) => (
                            <button
                              key={cIdx}
                              onClick={() => handleSendMessage(chip)}
                              style={{
                                backgroundColor: 'var(--bg-card)',
                                border: '1px solid var(--border-light)',
                                borderRadius: 'var(--radius-full)',
                                padding: '4px 10px',
                                fontSize: '0.74rem',
                                color: 'var(--text-primary)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '3px',
                                transition: 'all 0.15s ease'
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.borderColor = 'var(--accent-sage)';
                                e.currentTarget.style.backgroundColor = 'var(--bg-card-subtle)';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = 'var(--border-light)';
                                e.currentTarget.style.backgroundColor = 'var(--bg-card)';
                              }}
                            >
                              <span>{chip}</span>
                              <ChevronRight size={10} color="var(--accent-sage)" />
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {isUser && (
                      <div style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        backgroundColor: 'var(--text-primary)',
                        color: '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        marginTop: '2px'
                      }}>
                        <User size={14} />
                      </div>
                    )}
                  </div>
                );
              })
            )}

            {/* Thinking Indicator */}
            {isGenerating && (
              <div style={{ display: 'flex', gap: '10px', marginBottom: '16px', alignItems: 'flex-start' }}>
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--accent-sage-dark)',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <Sparkles size={14} />
                </div>
                <div style={{
                  backgroundColor: 'var(--bg-card)',
                  padding: '9px 14px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-light)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                    Searching reviews & computing debiased ratings...
                  </span>
                  <div style={{ display: 'flex', gap: '3px' }}>
                    <div style={{ width: '4px', height: '4px', borderRadius: '50%', backgroundColor: 'var(--accent-sage)', animation: 'pulse 1.2s infinite' }} />
                    <div style={{ width: '4px', height: '4px', borderRadius: '50%', backgroundColor: 'var(--accent-sage)', animation: 'pulse 1.2s infinite 0.2s' }} />
                    <div style={{ width: '4px', height: '4px', borderRadius: '50%', backgroundColor: 'var(--accent-sage)', animation: 'pulse 1.2s infinite 0.4s' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* BOTTOM FIXED INPUT BAR */}
        <div style={{
          flexShrink: 0,
          backgroundColor: 'var(--bg-card)',
          borderTop: '1px solid var(--border-light)',
          padding: '10px 16px',
          zIndex: 10
        }}>
          <div style={{ maxWidth: '780px', margin: '0 auto' }}>
            <div style={{
              display: 'flex',
              alignItems: 'flex-end',
              backgroundColor: 'var(--bg-primary)',
              border: '1px solid var(--border-light)',
              borderRadius: '24px',
              padding: '5px 8px 5px 14px',
              transition: 'border-color 0.2s ease',
            }}
            onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--accent-sage)'; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--border-light)'; }}
            >
              <textarea
                ref={textareaRef}
                value={inputText}
                onChange={handleTextareaChange}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything about electronic products, failure modes, or comparisons..."
                rows={1}
                style={{
                  width: '100%',
                  border: 'none',
                  outline: 'none',
                  background: 'transparent',
                  fontSize: '0.88rem',
                  color: 'var(--text-primary)',
                  resize: 'none',
                  maxHeight: '110px',
                  padding: '5px 0',
                  lineHeight: 1.4,
                  fontFamily: 'inherit'
                }}
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputText.trim() || isGenerating}
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: inputText.trim() && !isGenerating ? 'var(--text-primary)' : 'var(--bg-card-subtle)',
                  color: inputText.trim() && !isGenerating ? '#fff' : 'var(--text-muted)',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: inputText.trim() && !isGenerating ? 'pointer' : 'not-allowed',
                  marginLeft: '6px',
                  marginBottom: '1px',
                  flexShrink: 0,
                  transition: 'all 0.15s ease'
                }}
              >
                <Send size={13} />
              </button>
            </div>

            <div style={{
              fontSize: '0.66rem',
              color: 'var(--text-muted)',
              textAlign: 'center',
              marginTop: '4px'
            }}>
              ReviewGenAI analyzes real customer reviews across 8,866 electronics to deliver debiased, honest reality ratings.
            </div>
          </div>
        </div>
      </div>

      {/* Responsive Styles for Sidebar Drawer on Mobile */}
      <style>{`
        @media (max-width: 768px) {
          .assistant-sidebar {
            position: fixed !important;
            top: 70px !important;
            bottom: 0 !important;
            left: 0 !important;
            transform: translateX(-100%);
            box-shadow: 4px 0 16px rgba(0, 0, 0, 0.15);
          }
          .assistant-sidebar.open {
            transform: translateX(0);
          }
          .assistant-sidebar-close {
            display: flex !important;
          }
          .assistant-mobile-toggle {
            display: flex !important;
          }
        }
      `}</style>
    </div>
  );
}
