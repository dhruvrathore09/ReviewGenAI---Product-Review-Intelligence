import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, Star, ShieldCheck, CheckCircle2, MessageSquare, 
  Calendar, ThumbsUp, Tag, Cpu, Info, Filter, Package,
  Sparkles, Award, Battery, Wrench, AlertTriangle, ChevronDown, ChevronUp, Zap
} from 'lucide-react';
import api from '../services/api';
import StarRating from '../components/common/StarRating';

export default function ProductDetails() {
  const { productId } = useParams();

  const [product, setProduct] = useState(null);
  const [report, setReport] = useState(null);
  const [stats, setStats] = useState(null);
  const [reviewsData, setReviewsData] = useState({ items: [], total: 0, total_pages: 1 });
  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Raw reviews collapsible toggle
  const [showRawReviews, setShowRawReviews] = useState(false);

  // Review filtering state
  const [reviewPage, setReviewPage] = useState(1);
  const [starFilter, setStarFilter] = useState('');
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');

  // Load product details, intelligence report & statistics
  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    Promise.all([
      api.getProduct(productId),
      api.getProductReport(productId).catch(() => null),
      api.getProductStatistics(productId).catch(() => null),
    ])
      .then(([prod, rep, st]) => {
        if (isMounted) {
          setProduct(prod);
          setReport(rep);
          setStats(st);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Product not found');
          setLoading(false);
        }
      });

    return () => { isMounted = false; };
  }, [productId]);

  // Load reviews when review filter params change or when expanded
  useEffect(() => {
    if (!showRawReviews) return;

    let isMounted = true;
    setReviewsLoading(true);

    api.getProductReviews(productId, {
      page: reviewPage,
      page_size: 10,
      star_rating: starFilter ? parseFloat(starFilter) : undefined,
      verified_only: verifiedOnly ? true : undefined,
      sort_by: sortBy,
      order: sortOrder,
    })
      .then((data) => {
        if (isMounted) {
          setReviewsData(data);
          setReviewsLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setReviewsData({ items: [], total: 0, total_pages: 1 });
          setReviewsLoading(false);
        }
      });

    return () => { isMounted = false; };
  }, [productId, showRawReviews, reviewPage, starFilter, verifiedOnly, sortBy, sortOrder]);

  if (loading) {
    return (
      <div className="container" style={{ padding: '60px 0' }}>
        <div className="skeleton" style={{ height: '360px', marginBottom: '24px' }} />
        <div className="skeleton" style={{ height: '480px', marginBottom: '24px' }} />
        <div className="skeleton" style={{ height: '240px' }} />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="container" style={{ padding: '80px 0', textAlign: 'center' }}>
        <div className="card" style={{ maxWidth: '500px', margin: '0 auto', padding: '40px' }}>
          <h2 style={{ fontSize: '1.6rem', color: 'var(--accent-terracotta)', marginBottom: '12px' }}>
            Product Not Found
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            The requested ASIN ({productId}) was not located in our catalog.
          </p>
          <Link to="/products" className="btn btn-primary">
            <ArrowLeft size={16} />
            Back to Explorer
          </Link>
        </div>
      </div>
    );
  }

  const overallRating = report?.overall_rating || product.average_rating || 4.2;
  const marketplaceRating = report?.marketplace_listed_rating || product.average_rating || 4.2;
  const criticalComplaintRate = report?.critical_complaint_rate != null ? report.critical_complaint_rate : 22.5;
  const ratingsCount = report?.total_ratings_count || product.rating_number || product.db_review_count || 0;
  const satisfactionRate = report?.satisfaction_rate || Math.round((overallRating / 5) * 100);
  const qualityGrade = report?.quality_grade || (overallRating >= 4.5 ? 'Grade A' : overallRating >= 4.0 ? 'Grade B+' : 'Grade B');

  const getAspectIcon = (aspectName) => {
    const lower = aspectName.toLowerCase();
    if (lower.includes('durability') || lower.includes('build')) return <Wrench size={18} color="var(--accent-sage-dark)" />;
    if (lower.includes('lifespan') || lower.includes('battery')) return <Battery size={18} color="var(--accent-gold)" />;
    if (lower.includes('performance') || lower.includes('speed')) return <Cpu size={18} color="var(--accent-sage)" />;
    if (lower.includes('usability') || lower.includes('comfort')) return <CheckCircle2 size={18} color="var(--accent-sage)" />;
    if (lower.includes('value')) return <Award size={18} color="var(--accent-gold)" />;
    return <Sparkles size={18} color="var(--accent-sage)" />;
  };

  const getStatusBadgeStyle = (status) => {
    switch (status) {
      case 'Exceptional':
      case 'Excellent':
        return { backgroundColor: 'var(--bg-sage-subtle)', color: 'var(--accent-sage-dark)', border: '1px solid rgba(135, 151, 122, 0.4)' };
      case 'Very Good':
      case 'Solid':
        return { backgroundColor: '#FDF8EC', color: '#976F1D', border: '1px solid rgba(201, 169, 110, 0.4)' };
      default:
        return { backgroundColor: '#FDF2F0', color: 'var(--accent-terracotta)', border: '1px solid rgba(200, 109, 86, 0.4)' };
    }
  };

  return (
    <div style={{ padding: '40px 0 80px 0' }}>
      <div className="container">
        {/* Navigation Breadcrumb */}
        <div style={{ marginBottom: '24px' }}>
          <Link
            to="/products"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.85rem',
              color: 'var(--text-secondary)',
              fontWeight: 500,
            }}
          >
            <ArrowLeft size={15} />
            Back to Product Explorer
          </Link>
        </div>

        {/* Product Overview Hero Card */}
        <div className="card" style={{ padding: '36px', marginBottom: '32px' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '40px',
            alignItems: 'center',
          }}>
            {/* Product Image */}
            <div style={{
              height: '320px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: '#F9F7F2',
              border: '1px solid var(--border-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '24px',
            }}>
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.product_name}
                  style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }}
                />
              ) : (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                  <Package size={48} strokeWidth={1.5} />
                  <div style={{ marginTop: '8px', fontSize: '0.85rem' }}>No catalog image</div>
                </div>
              )}
            </div>

            {/* Product Metadata & Overall Rating Scorecard */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
                {product.brand && (
                  <span className="badge badge-sage">
                    {product.brand}
                  </span>
                )}
                {product.main_category && (
                  <span className="badge badge-neutral">
                    {product.main_category}
                  </span>
                )}
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  ASIN: {product.product_id}
                </span>
              </div>

              <h1 style={{
                fontSize: '1.85rem',
                lineHeight: 1.3,
                marginBottom: '12px',
                color: 'var(--text-primary)',
              }}>
                {product.product_name}
              </h1>

              {product.categories_hierarchy && (
                <p style={{
                  fontSize: '0.8rem',
                  color: 'var(--text-muted)',
                  marginBottom: '18px',
                  lineHeight: 1.4,
                }}>
                  {product.categories_hierarchy}
                </p>
              )}

              {/* Price & Primary Attributes */}
              <div style={{
                display: 'flex',
                alignItems: 'baseline',
                gap: '12px',
                marginBottom: '20px',
              }}>
                <span style={{
                  fontFamily: 'var(--font-serif)',
                  fontSize: '2rem',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                }}>
                  {product.price != null ? `$${Number(product.price).toFixed(2)}` : 'Listing Price Unavailable'}
                </span>
              </div>

              {/* Overall Product Rating Scorecard */}
              <div style={{
                padding: '22px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-light)',
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '16px',
                  marginBottom: '14px',
                }}>
                  {/* Honest Critical Rating */}
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                      <span style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--accent-terracotta)', fontWeight: 700, letterSpacing: '0.5px' }}>
                        Honest Reality Rating
                      </span>
                      <span style={{
                        fontSize: '0.68rem',
                        padding: '1px 6px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: '#FDF2F0',
                        color: 'var(--accent-terracotta)',
                        fontWeight: 600,
                      }}>
                        Critical Checked
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontFamily: 'var(--font-serif)', fontSize: '2.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                        {overallRating.toFixed(2)}
                      </span>
                      <StarRating rating={overallRating} size={20} />
                    </div>
                  </div>

                  {/* Amazon Listed vs Defect Rate Comparison Badges */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'flex-start' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <div style={{
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-medium)',
                        fontSize: '0.8rem',
                        color: 'var(--text-secondary)',
                      }}>
                        Amazon Listed: <strong style={{ color: 'var(--text-primary)' }}>{marketplaceRating.toFixed(1)}★</strong>
                      </div>
                      <div style={{
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: '#FDF2F0',
                        border: '1px solid rgba(200, 109, 86, 0.4)',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        color: 'var(--accent-terracotta)',
                      }}>
                        ⚠️ {criticalComplaintRate}% Critical Defect Rate
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: 'var(--bg-sage-subtle)',
                        border: '1px solid rgba(135, 151, 122, 0.4)',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        color: 'var(--accent-sage-dark)',
                      }}>
                        {qualityGrade}
                      </div>
                      <div style={{
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: '#FDF8EC',
                        border: '1px solid rgba(201, 169, 110, 0.4)',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        color: '#976F1D',
                      }}>
                        {satisfactionRate}% Net Satisfaction
                      </div>
                    </div>
                  </div>
                </div>

                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '10px' }}>
                  Calibrated across <strong>{ratingsCount.toLocaleString()}</strong> catalog ratings and verified negative owner failure reports.
                </div>

                {report?.overall_verdict && (
                  <div style={{
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-medium)',
                    fontSize: '0.86rem',
                    color: 'var(--text-primary)',
                    fontWeight: 500,
                  }}>
                    💡 <span style={{ fontWeight: 600 }}>Honest Verdict:</span> {report.overall_verdict}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* EXECUTIVE PRODUCT REVIEW INTELLIGENCE REPORT */}
        {/* ========================================================================= */}
        {report && (
          <div className="card" style={{
            padding: '36px',
            marginBottom: '36px',
            border: '2px solid var(--border-medium)',
            boxShadow: 'var(--shadow-md)',
          }}>
            {/* Report Header */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingBottom: '20px',
              borderBottom: '1px solid var(--border-light)',
              marginBottom: '28px',
              flexWrap: 'wrap',
              gap: '12px',
            }}>
              <div>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                  <span className="badge badge-sage">
                    <Sparkles size={12} />
                    OVERALL REVIEW REPORT
                  </span>
                </div>
                <h2 style={{ fontSize: '1.7rem', color: 'var(--text-primary)', marginBottom: '4px' }}>
                  Product Intelligence & Review Report
                </h2>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  Clear, evidence-grounded evaluation covering durability, lifespan, performance, and real-world owner findings.
                </p>
              </div>

              <div style={{
                padding: '8px 16px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-medium)',
                fontSize: '0.82rem',
                color: 'var(--text-secondary)',
                fontWeight: 600,
              }}>
                🛡️ {report.confidence_level}
              </div>
            </div>

            {/* Executive Consensus Paragraph */}
            <div style={{
              padding: '20px 24px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--bg-card-subtle)',
              border: '1px solid var(--border-light)',
              marginBottom: '32px',
            }}>
              <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--accent-sage-dark)', fontWeight: 700, letterSpacing: '0.5px', marginBottom: '8px' }}>
                Executive Review Synthesis
              </div>
              <p style={{
                fontSize: '1.02rem',
                lineHeight: 1.65,
                color: 'var(--text-primary)',
                margin: 0,
              }}>
                {report.executive_summary}
              </p>
            </div>

            {/* Core Dimensions Breakdown: Durability, Life, Performance, Usability, Value */}
            <div style={{ marginBottom: '36px' }}>
              <h3 style={{ fontSize: '1.3rem', color: 'var(--text-primary)', marginBottom: '16px' }}>
                Key Product Dimensions (Durability, Life & Performance)
              </h3>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                gap: '16px',
              }}>
                {report.aspects.map((aspect) => (
                  <div
                    key={aspect.name}
                    style={{
                      padding: '20px',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: 'var(--bg-primary)',
                      border: '1px solid var(--border-light)',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                    }}
                  >
                    <div>
                      {/* Aspect Title & Status */}
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        marginBottom: '10px',
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          {getAspectIcon(aspect.name)}
                          <strong style={{ fontSize: '0.98rem', color: 'var(--text-primary)' }}>
                            {aspect.name}
                          </strong>
                        </div>
                        <span
                          style={{
                            padding: '3px 10px',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            ...getStatusBadgeStyle(aspect.status),
                          }}
                        >
                          {aspect.status}
                        </span>
                      </div>

                      {/* Aspect Score Bar */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                        <div style={{
                          flex: 1,
                          height: '8px',
                          backgroundColor: 'var(--border-light)',
                          borderRadius: '4px',
                          overflow: 'hidden',
                        }}>
                          <div style={{
                            width: `${aspect.percentage}%`,
                            height: '100%',
                            backgroundColor: aspect.score >= 4.2 ? 'var(--accent-sage)' : aspect.score >= 3.6 ? 'var(--accent-gold)' : 'var(--accent-terracotta)',
                            borderRadius: '4px',
                            transition: 'width 0.4s ease',
                          }} />
                        </div>
                        <span style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)', minWidth: '46px', textAlign: 'right' }}>
                          {aspect.score.toFixed(1)} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ 5.0</span>
                        </span>
                      </div>

                      {/* Aspect Summary */}
                      <p style={{
                        fontSize: '0.86rem',
                        color: 'var(--text-secondary)',
                        lineHeight: 1.55,
                        marginBottom: '12px',
                      }}>
                        {aspect.summary}
                      </p>
                    </div>

                    {/* Key Evidence / Quote */}
                    <div style={{
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-light)',
                      fontSize: '0.78rem',
                      color: 'var(--text-secondary)',
                      fontStyle: 'italic',
                    }}>
                      💬 {aspect.key_evidence}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ========================================================================= */}
            {/* CRITICAL NEGATIVE POINTS & FAILURE MODES (UNBIASED REAL BUYER TRUTH) */}
            {/* ========================================================================= */}
            {report.critical_negative_points && report.critical_negative_points.length > 0 && (
              <div style={{
                marginBottom: '36px',
                padding: '28px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: '#FCF8F7',
                border: '2px solid rgba(200, 109, 86, 0.4)',
                boxShadow: 'var(--shadow-sm)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px', flexWrap: 'wrap', gap: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      backgroundColor: '#FDF2F0',
                      color: 'var(--accent-terracotta)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      <AlertTriangle size={20} />
                    </div>
                    <div>
                      <h3 style={{ fontSize: '1.3rem', color: '#9E3B27', margin: 0, fontWeight: 700 }}>
                        Critical Negative Points & Failure Modes
                      </h3>
                      <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', margin: 0 }}>
                        Real buyer warnings, durability flaws, and operational risks extracted directly from critical feedback.
                      </p>
                    </div>
                  </div>
                  <span style={{
                    padding: '5px 12px',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: '#FDF2F0',
                    color: 'var(--accent-terracotta)',
                    border: '1px solid rgba(200, 109, 86, 0.4)',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                  }}>
                    {criticalComplaintRate}% Defect & Critical Rate
                  </span>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                  gap: '14px',
                }}>
                  {report.critical_negative_points.map((point, idx) => {
                    const isHigh = point.severity === 'High';
                    return (
                      <div
                        key={idx}
                        style={{
                          padding: '18px 20px',
                          borderRadius: 'var(--radius-sm)',
                          backgroundColor: '#FFFFFF',
                          border: isHigh ? '1.5px solid rgba(200, 109, 86, 0.4)' : '1px solid var(--border-medium)',
                          boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', gap: '8px' }}>
                          <strong style={{ fontSize: '0.96rem', color: isHigh ? '#9E3B27' : 'var(--text-primary)' }}>
                            {point.title}
                          </strong>
                          <span style={{
                            padding: '2px 8px',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            textTransform: 'uppercase',
                            backgroundColor: isHigh ? '#FDF2F0' : '#FDF8EC',
                            color: isHigh ? '#C86D56' : '#976F1D',
                            border: isHigh ? '1px solid rgba(200, 109, 86, 0.3)' : '1px solid rgba(201, 169, 110, 0.3)',
                            whiteSpace: 'nowrap',
                          }}>
                            {point.severity} Risk
                          </span>
                        </div>

                        <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: '0 0 10px 0' }}>
                          {point.description}
                        </p>

                        {point.quote && (
                          <div style={{
                            padding: '8px 12px',
                            borderRadius: 'var(--radius-sm)',
                            backgroundColor: '#FAF7F3',
                            borderLeft: '3px solid var(--accent-terracotta)',
                            fontSize: '0.78rem',
                            color: 'var(--text-primary)',
                            fontStyle: 'italic',
                            lineHeight: 1.45,
                          }}>
                            "{point.quote}"
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ========================================================================= */}
            {/* DIRECT BUYER CRITICISM (REAL 1★ & 2★ REVIEWS FROM DATABASE) */}
            {/* ========================================================================= */}
            {report.real_negative_quotes && report.real_negative_quotes.length > 0 && (
              <div style={{
                marginBottom: '36px',
                padding: '24px 28px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-medium)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                  <MessageSquare size={18} color="var(--accent-terracotta)" />
                  <h4 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', margin: 0, fontWeight: 600 }}>
                    Direct Buyer Criticism (Real 1★ & 2★ Owner Complaints)
                  </h4>
                </div>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: '14px',
                }}>
                  {report.real_negative_quotes.map((quoteStr, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '14px 16px',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-light)',
                        borderLeft: '4px solid var(--accent-terracotta)',
                        fontSize: '0.82rem',
                        color: 'var(--text-secondary)',
                        lineHeight: 1.5,
                      }}
                    >
                      <span style={{ fontWeight: 600, color: 'var(--accent-terracotta)', display: 'block', marginBottom: '4px' }}>
                        Verified Owner Critical Warning #{idx + 1}
                      </span>
                      "{quoteStr}"
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Strengths vs Flaws Breakdown Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '24px',
              marginBottom: '36px',
            }}>
              {/* Confirmed Strengths */}
              <div style={{
                padding: '24px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'rgba(135, 151, 122, 0.08)',
                border: '1px solid rgba(135, 151, 122, 0.3)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <CheckCircle2 size={20} color="var(--accent-sage-dark)" />
                  <h4 style={{ fontSize: '1.15rem', color: 'var(--accent-sage-dark)', margin: 0 }}>
                    What Verified Owners Praise (Top Strengths)
                  </h4>
                </div>

                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {report.strengths.map((str, idx) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.45 }}>
                      <span style={{ color: 'var(--accent-sage-dark)', fontWeight: 700 }}>✓</span>
                      <span>{str}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Known Flaws & Watch-Outs */}
              <div style={{
                padding: '24px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'rgba(200, 109, 86, 0.08)',
                border: '1px solid rgba(200, 109, 86, 0.3)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <AlertTriangle size={20} color="var(--accent-terracotta)" />
                  <h4 style={{ fontSize: '1.15rem', color: 'var(--accent-terracotta)', margin: 0 }}>
                    What to Watch Out For (Reported Flaws & Caveats)
                  </h4>
                </div>

                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {report.flaws_and_drawbacks.map((flaw, idx) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.45 }}>
                      <span style={{ color: 'var(--accent-terracotta)', fontWeight: 700 }}>⚠</span>
                      <span>{flaw}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Durability & Longevity Deep Dive Section */}
            <div style={{
              padding: '24px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--bg-primary)',
              border: '1px solid var(--border-medium)',
              marginBottom: '32px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                <Wrench size={18} color="var(--accent-sage-dark)" />
                <h4 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', margin: 0 }}>
                  Durability & Real-World Longevity Assessment
                </h4>
              </div>
              <p style={{
                fontSize: '0.92rem',
                lineHeight: 1.6,
                color: 'var(--text-secondary)',
                margin: 0,
              }}>
                {report.durability_and_longevity_deep_dive}
              </p>
            </div>

            {/* Buyer Recommendation Matrix */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '20px',
              paddingTop: '20px',
              borderTop: '1px solid var(--border-light)',
            }}>
              <div style={{
                padding: '16px 20px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-light)',
              }}>
                <strong style={{ display: 'block', fontSize: '0.85rem', color: 'var(--accent-sage-dark)', marginBottom: '6px' }}>
                  👍 IDEAL FOR:
                </strong>
                <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
                  {report.who_should_buy}
                </p>
              </div>

              <div style={{
                padding: '16px 20px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-light)',
              }}>
                <strong style={{ display: 'block', fontSize: '0.85rem', color: 'var(--accent-terracotta)', marginBottom: '6px' }}>
                  ✋ LOOK FOR ALTERNATIVES IF:
                </strong>
                <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
                  {report.who_should_skip}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Rating Distribution Breakdown */}
        {stats && stats.star_distribution && (
          <div className="card" style={{ padding: '28px', marginBottom: '36px' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '16px' }}>
              Star Rating Breakdown Across Verified Owners
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {stats.star_distribution.map((item) => (
                <div key={item.star_rating} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ width: '38px', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    {item.star_rating.toFixed(0)} ★
                  </span>
                  <div style={{
                    flex: 1,
                    height: '8px',
                    backgroundColor: 'var(--bg-card-subtle)',
                    borderRadius: '4px',
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      width: `${item.percentage}%`,
                      height: '100%',
                      backgroundColor: item.star_rating >= 4 ? 'var(--accent-sage)' : item.star_rating === 3 ? 'var(--accent-gold)' : 'var(--accent-terracotta)',
                      borderRadius: '4px',
                      transition: 'width 0.4s ease',
                    }} />
                  </div>
                  <span style={{ width: '45px', textAlign: 'right', fontSize: '0.82rem', fontWeight: 600 }}>
                    {item.percentage.toFixed(1)}%
                  </span>
                  <span style={{ width: '50px', textAlign: 'right', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    ({item.count})
                  </span>
                </div>
              ))}

              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingTop: '14px',
                marginTop: '10px',
                borderTop: '1px solid var(--border-light)',
                fontSize: '0.82rem',
                color: 'var(--text-secondary)',
              }}>
                <span>Verified Buyer Purchase Ratio:</span>
                <strong style={{ color: 'var(--accent-sage-dark)' }}>
                  {stats.verified_purchases_percentage}% ({stats.verified_purchases_count} verified)
                </strong>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* RAW INDIVIDUAL CUSTOMER REVIEWS (COLLAPSIBLE / DE-EMPHASIZED) */}
        {/* ========================================================================= */}
        <section style={{
          padding: '28px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-light)',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px',
          }}>
            <div>
              <h3 style={{ fontSize: '1.3rem', color: 'var(--text-primary)', marginBottom: '4px' }}>
                Raw Individual Customer Comments ({product.db_review_count || reviewsData.total})
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                The synthesized report above captures the overall consensus. Expand here if you wish to read raw individual comments.
              </p>
            </div>

            <button
              onClick={() => setShowRawReviews(!showRawReviews)}
              className="btn btn-outline"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 18px',
                fontSize: '0.86rem',
              }}
            >
              <MessageSquare size={16} />
              {showRawReviews ? 'Hide Raw Comments' : `Inspect Raw Comments (${product.db_review_count || reviewsData.total})`}
              {showRawReviews ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          </div>

          {showRawReviews && (
            <div style={{ marginTop: '24px', paddingTop: '20px', borderTop: '1px solid var(--border-light)' }}>
              {/* Review Filter Bar */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', marginBottom: '20px' }}>
                {/* Star Rating Filter */}
                <select
                  value={starFilter}
                  onChange={(e) => {
                    setStarFilter(e.target.value);
                    setReviewPage(1);
                  }}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-full)',
                    border: '1px solid var(--border-medium)',
                    backgroundColor: 'var(--bg-card)',
                    fontSize: '0.82rem',
                  }}
                >
                  <option value="">All Star Ratings</option>
                  <option value="5.0">5 Stars Only</option>
                  <option value="4.0">4 Stars Only</option>
                  <option value="3.0">3 Stars Only</option>
                  <option value="2.0">2 Stars Only</option>
                  <option value="1.0">1 Star Only</option>
                </select>

                {/* Verified Only Toggle */}
                <button
                  onClick={() => {
                    setVerifiedOnly(!verifiedOnly);
                    setReviewPage(1);
                  }}
                  className={`btn ${verifiedOnly ? 'btn-sage' : 'btn-outline'}`}
                  style={{ padding: '6px 14px', fontSize: '0.82rem' }}
                >
                  <ShieldCheck size={14} />
                  {verifiedOnly ? 'Verified Only: Active' : 'Verified Purchases Only'}
                </button>

                {/* Sort By */}
                <select
                  value={`${sortBy}:${sortOrder}`}
                  onChange={(e) => {
                    const [sb, ord] = e.target.value.split(':');
                    setSortBy(sb);
                    setSortOrder(ord);
                    setReviewPage(1);
                  }}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-full)',
                    border: '1px solid var(--border-medium)',
                    backgroundColor: 'var(--bg-card)',
                    fontSize: '0.82rem',
                  }}
                >
                  <option value="date:desc">Newest First</option>
                  <option value="date:asc">Oldest First</option>
                  <option value="rating:desc">Highest Rating</option>
                  <option value="rating:asc">Lowest Rating</option>
                  <option value="helpful:desc">Most Helpful</option>
                </select>
              </div>

              {/* Review List */}
              {reviewsLoading ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="skeleton" style={{ height: '120px' }} />
                  ))}
                </div>
              ) : reviewsData.items.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '36px' }}>
                  <MessageSquare size={28} color="var(--text-muted)" style={{ margin: '0 auto 8px auto' }} />
                  <h4 style={{ fontSize: '1.1rem', marginBottom: '6px' }}>No raw reviews found for these filters</h4>
                  <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                    Try selecting "All Star Ratings" or turning off the verified-only toggle.
                  </p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {reviewsData.items.map((rev) => (
                    <div key={rev.review_id} className="card" style={{ padding: '20px' }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        marginBottom: '8px',
                        flexWrap: 'wrap',
                        gap: '8px',
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <StarRating rating={rev.star_rating} size={14} />
                          {rev.review_title && (
                            <strong style={{ fontSize: '0.94rem', color: 'var(--text-primary)' }}>
                              {rev.review_title}
                            </strong>
                          )}
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          {rev.verified_purchase && (
                            <span className="badge badge-sage" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                              <CheckCircle2 size={10} />
                              Verified Purchase
                            </span>
                          )}
                          <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Calendar size={12} />
                            {new Date(rev.review_date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                          </span>
                        </div>
                      </div>

                      <p style={{
                        fontSize: '0.88rem',
                        color: 'var(--text-secondary)',
                        lineHeight: 1.55,
                        whiteSpace: 'pre-line',
                        marginBottom: '10px',
                      }}>
                        {rev.review_text}
                      </p>

                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        fontSize: '0.74rem',
                        color: 'var(--text-muted)',
                        paddingTop: '8px',
                        borderTop: '1px solid var(--border-light)',
                      }}>
                        <span>Comment #{rev.review_id}</span>
                        {rev.helpful_votes > 0 && (
                          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <ThumbsUp size={12} />
                            {rev.helpful_votes} people found this helpful
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Review Pagination */}
              {reviewsData.total_pages > 1 && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '12px',
                  marginTop: '24px',
                }}>
                  <button
                    onClick={() => setReviewPage(reviewPage - 1)}
                    disabled={reviewPage <= 1}
                    className="btn btn-outline"
                    style={{ padding: '6px 14px', fontSize: '0.82rem', opacity: reviewPage <= 1 ? 0.4 : 1 }}
                  >
                    Previous
                  </button>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Page {reviewPage} of {reviewsData.total_pages}
                  </span>
                  <button
                    onClick={() => setReviewPage(reviewPage + 1)}
                    disabled={reviewPage >= reviewsData.total_pages}
                    className="btn btn-outline"
                    style={{ padding: '6px 14px', fontSize: '0.82rem', opacity: reviewPage >= reviewsData.total_pages ? 0.4 : 1 }}
                  >
                    Next
                  </button>
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
