import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Search, ArrowRight, ShieldCheck, Cpu, Database, BarChart2, 
  Star, Sparkles, CheckCircle2, Smartphone, Laptop, Camera, 
  Headphones, Watch, Wrench, Briefcase, Car, Music, Gamepad2, 
  Navigation, Layers, ChevronDown, ChevronUp, Package, ArrowUpRight, Volume2,
  HardDrive, Tv, Plug
} from 'lucide-react';
import api, { API_BASE_URL } from '../services/api';
import StatCard from '../components/common/StatCard';

export default function Home() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [overview, setOverview] = useState(null);
  const [showAllCategories, setShowAllCategories] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    api.getDashboardOverview()
      .then((overviewData) => {
        if (isMounted) {
          setOverview(overviewData);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to load platform data');
          setLoading(false);
        }
      });

    return () => { isMounted = false; };
  }, []);

  const CATEGORY_SEARCH_PATTERNS = [
    {
      category: 'Laptops & Notebooks',
      regex: /\b(laptops?|notebooks?|chromebooks?|macbooks?|ultrabooks?)\b/i,
    },
    {
      category: 'Smartphones & Mobiles',
      regex: /\b(smartphones?|mobiles?|cell\s*phones?|phones?)\b/i,
    },
    {
      category: 'Headphones & Earbuds',
      regex: /\b(headphones?|earbuds?|earphones?|headsets?)\b/i,
    },
    {
      category: 'Cameras & Photography',
      regex: /\b(cameras?|camcorders?|dslrs?|webcams?|photography)\b/i,
    },
    {
      category: 'Hard Disks & Storage',
      regex: /\b(hard\s*disks?|hard\s*drives?|ssds?|flash\s*drives?|thumb\s*drives?|memory\s*cards?|microsd|storage)\b/i,
    },
    {
      category: 'Home Audio & Speakers',
      regex: /\b(speakers?|soundbars?|subwoofers?|home\s*audio|home\s*theater)\b/i,
    },
    {
      category: 'Smart Home & Devices',
      regex: /\b(smart\s*homes?|amazon\s*devices?|echo|fire\s*tv|kindles?)\b/i,
    },
    {
      category: 'Cables & Power Accessories',
      regex: /\b(cables?|hdmi|chargers?|power\s*adapters?|power\s*strips?)\b/i,
    },
  ];

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (!query) {
      navigate('/products');
      return;
    }

    let matchedCategory = null;
    let remainingTerm = query;

    for (const item of CATEGORY_SEARCH_PATTERNS) {
      if (item.regex.test(query)) {
        matchedCategory = item.category;
        remainingTerm = query.replace(item.regex, '').replace(/\s+/g, ' ').trim();
        break;
      }
    }

    if (matchedCategory && remainingTerm) {
      // e.g. "HP laptop" -> category="Laptops & Notebooks" and q="HP"
      navigate(`/products?category=${encodeURIComponent(matchedCategory)}&q=${encodeURIComponent(remainingTerm)}`);
    } else if (matchedCategory && !remainingTerm) {
      // e.g. "laptops", "smartphones", "hard disk" -> category="Laptops & Notebooks"
      navigate(`/products?category=${encodeURIComponent(matchedCategory)}`);
    } else {
      // e.g. "Sony", "SanDisk", "MacBook", "B075X8471B"
      navigate(`/products?q=${encodeURIComponent(query)}`);
    }
  };

  const getCategoryIcon = (name) => {
    const lower = name.toLowerCase();
    if (lower.includes('headphone') || lower.includes('earbud')) return <Headphones size={20} color="var(--accent-sage)" />;
    if (lower.includes('cell phone') || lower.includes('phone') || lower.includes('mobile')) return <Smartphone size={20} color="var(--accent-sage)" />;
    if (lower.includes('laptop') || lower.includes('notebook')) return <Laptop size={20} color="var(--accent-sage)" />;
    if (lower.includes('camera') || lower.includes('photo')) return <Camera size={20} color="var(--accent-sage)" />;
    if (lower.includes('hard disk') || lower.includes('storage') || lower.includes('drive')) return <HardDrive size={20} color="var(--accent-sage)" />;
    if (lower.includes('audio') || lower.includes('speaker') || lower.includes('theater')) return <Volume2 size={20} color="var(--accent-sage)" />;
    if (lower.includes('smart home') || lower.includes('amazon device') || lower.includes('tv')) return <Tv size={20} color="var(--accent-gold)" />;
    if (lower.includes('cable') || lower.includes('power') || lower.includes('charger')) return <Plug size={20} color="var(--accent-sage)" />;
    return <Package size={20} color="var(--accent-sage)" />;
  };

  const allCategories = overview?.top_categories || [
    { category: 'Laptops & Notebooks', product_count: 1731, review_count: 383 },
    { category: 'Smartphones & Mobiles', product_count: 1019, review_count: 1276 },
    { category: 'Cameras & Photography', product_count: 444, review_count: 441 },
    { category: 'Hard Disks & Storage', product_count: 422, review_count: 435 },
    { category: 'Home Audio & Speakers', product_count: 411, review_count: 677 },
    { category: 'Cables & Power Accessories', product_count: 386, review_count: 626 },
    { category: 'Headphones & Earbuds', product_count: 324, review_count: 538 },
    { category: 'Smart Home & Devices', product_count: 112, review_count: 646 },
  ];
  const displayedCategories = showAllCategories ? allCategories : allCategories.slice(0, 8);

  return (
    <div>
      {/* Editorial Hero Section */}
      <section style={{
        padding: '72px 0 64px 0',
        borderBottom: '1px solid var(--border-light)',
        background: 'linear-gradient(180deg, rgba(243, 239, 230, 0.6) 0%, rgba(248, 246, 240, 1) 100%)',
      }}>
        <div className="container" style={{ textAlign: 'center', maxWidth: '860px' }}>
          <div style={{ display: 'inline-flex', marginBottom: '20px' }}>
            <span className="badge badge-sage">
              <Sparkles size={12} />
              PRODUCT REVIEW INTELLIGENCE
            </span>
          </div>

          <h1 style={{
            fontSize: 'clamp(1.9rem, 5vw, 3.4rem)',
            lineHeight: 1.15,
            marginBottom: '20px',
            color: 'var(--text-primary)',
          }}>
            Clear intelligence from thousands of voices.
          </h1>

          <p style={{
            fontSize: 'clamp(0.95rem, 2vw, 1.15rem)',
            color: 'var(--text-secondary)',
            lineHeight: 1.6,
            marginBottom: '36px',
            maxWidth: '680px',
            margin: '0 auto 36px auto',
          }}>
            Transforming unstructured customer feedback into evidence-grounded insights.
            Evaluate genuine ratings, sentiment distributions, and product flaws without reading thousands of reviews.
          </p>

          {/* Search Box */}
          <form
            onSubmit={handleSearchSubmit}
            style={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-medium)',
              borderRadius: 'var(--radius-full)',
              padding: '8px 10px 8px 24px',
              boxShadow: 'var(--shadow-md)',
              maxWidth: '620px',
              margin: '0 auto',
            }}
          >
            <Search size={20} color="var(--text-muted)" style={{ marginRight: '12px', flexShrink: 0 }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search..."
              style={{
                width: '100%',
                border: 'none',
                background: 'transparent',
                fontSize: '0.98rem',
                color: 'var(--text-primary)',
                outline: 'none',
              }}
            />
            <button type="submit" className="btn btn-primary" style={{ padding: '10px 24px' }}>
              Search
            </button>
          </form>
        </div>
      </section>

      {/* Platform Summary Metrics Banner */}
      <section style={{ padding: '48px 0', borderBottom: '1px solid var(--border-light)' }}>
        <div className="container">
          {loading ? (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '20px',
            }}>
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="skeleton" style={{ height: '120px' }} />
              ))}
            </div>
          ) : error ? (
            <div className="card" style={{ textAlign: 'center', color: 'var(--accent-terracotta)', padding: '24px' }}>
              Could not connect to backend service at <code style={{ background: 'rgba(0,0,0,0.06)', padding: '2px 6px', borderRadius: '4px' }}>{API_BASE_URL}</code>.
            </div>
          ) : overview ? (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '20px',
            }}>
              <StatCard
                label="Electronic Products"
                value={overview.total_products.toLocaleString()}
                subtext="Verified catalog entries"
                icon={Database}
                accent="sage"
              />
              <StatCard
                label="Customer Reviews"
                value={overview.total_reviews.toLocaleString()}
                subtext="Scrubbed and structured"
                icon={BarChart2}
                accent="gold"
              />
              <StatCard
                label="Platform Average"
                value={`${overview.overall_average_review_rating.toFixed(2)} ★`}
                subtext="Across all collected reviews"
                icon={Star}
                accent="gold"
              />
              <StatCard
                label="Verified Purchases"
                value={`${overview.verified_reviews_percentage}%`}
                subtext={`${overview.total_verified_reviews.toLocaleString()} verified buyers`}
                icon={ShieldCheck}
                accent="sage"
              />
            </div>
          ) : null}
        </div>
      </section>

      {/* Complete Product Category Section */}
      {overview && (
        <section style={{
          padding: '64px 0',
          backgroundColor: 'var(--bg-card-subtle)',
          borderBottom: '1px solid var(--border-light)',
        }}>
          <div className="container">
            <div style={{
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'space-between',
              marginBottom: '32px',
              flexWrap: 'wrap',
              gap: '16px',
            }}>
              <div>
                <span className="badge badge-sage" style={{ marginBottom: '8px' }}>
                  Catalog Taxonomy
                </span>
                <h2 style={{ fontSize: '2.2rem', color: 'var(--text-primary)' }}>
                  Explore by Product Category
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginTop: '4px' }}>
                  Discover electronics organized across all {allCategories.length} verified categories stored in our database.
                </p>
              </div>

              <button
                onClick={() => setShowAllCategories(!showAllCategories)}
                className="btn btn-outline"
                style={{ fontSize: '0.85rem', padding: '8px 18px' }}
              >
                {showAllCategories ? (
                  <>Show Top Categories <ChevronUp size={15} /></>
                ) : (
                  <>View All {allCategories.length} Categories <ChevronDown size={15} /></>
                )}
              </button>
            </div>

            {/* Category Card Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(210px, 1fr))',
              gap: '14px',
            }}>
              {displayedCategories.map((cat) => (
                <div
                  key={cat.category}
                  onClick={() => navigate(`/products?category=${encodeURIComponent(cat.category)}`)}
                  className="card"
                  style={{
                    padding: '20px',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '16px',
                    cursor: 'pointer',
                    backgroundColor: 'var(--bg-card)',
                    transition: 'all var(--transition-normal)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.borderColor = 'var(--accent-sage)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.borderColor = 'var(--border-light)';
                  }}
                >
                  <div style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-sage-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}>
                    {getCategoryIcon(cat.category)}
                  </div>

                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontWeight: 600,
                      fontSize: '0.98rem',
                      color: 'var(--text-primary)',
                      marginBottom: '4px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}>
                      <span>{cat.category}</span>
                      {cat.isCurated && (
                        <span className="badge badge-sage" style={{ fontSize: '0.65rem', padding: '1px 6px' }}>
                          Curated
                        </span>
                      )}
                    </div>

                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '0.78rem',
                      color: 'var(--text-muted)',
                    }}>
                      <span>{cat.product_count.toLocaleString()} products</span>
                      <span>•</span>
                      <span>{cat.review_count.toLocaleString()} reviews</span>
                    </div>
                  </div>

                  <ArrowUpRight size={16} color="var(--text-muted)" style={{ flexShrink: 0, marginTop: '2px' }} />
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Platform Pillars / Architecture Philosophy */}
      <section style={{ padding: '72px 0' }}>
        <div className="container" style={{ textAlign: 'center', maxWidth: '900px' }}>
          <span className="badge badge-sage" style={{ marginBottom: '12px' }}>
            Data Integrity First
          </span>
          <h2 style={{ fontSize: '2.4rem', marginBottom: '18px' }}>
            Architected for verifiable evidence, not hallucinations.
          </h2>
          <p style={{
            fontSize: '1.05rem',
            color: 'var(--text-secondary)',
            marginBottom: '48px',
            lineHeight: 1.6,
          }}>
            Unlike generic chatbots that summarize imaginary consensus, our platform couples relational PostgreSQL aggregation with strict provenance tracking.
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '24px',
            textAlign: 'left',
          }}>
            <div className="card">
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: 'var(--bg-sage-subtle)',
                color: 'var(--accent-sage-dark)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '16px',
              }}>
                <CheckCircle2 size={20} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>Zero Synthetic Data</h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Every calculation and statistic is computed directly from genuine customer reviews collected from Amazon Electronics 2023.
              </p>
            </div>

            <div className="card">
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: 'var(--bg-gold-subtle)',
                color: 'var(--accent-gold-dark)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '16px',
              }}>
                <BarChart2 size={20} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>Dual-Rating Disclosures</h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                We clearly separate broad marketplace catalog averages from the exact distributions calculated across collected reviews.
              </p>
            </div>

            <div className="card">
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: 'var(--bg-card-subtle)',
                color: 'var(--text-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '16px',
              }}>
                <Cpu size={20} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>Calibrated ML Models</h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Level 5 Calibrated Linear SVM and Balanced Logistic Regression models trained on text-only features to avoid star-rating leakage.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
