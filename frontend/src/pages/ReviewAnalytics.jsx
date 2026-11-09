import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Legend 
} from 'recharts';
import { 
  BarChart3, Database, ShieldCheck, Star, Layers, Award, 
  Cpu, Battery, Wrench, Sparkles, CheckCircle2, AlertTriangle, 
  ArrowRight, ExternalLink, Zap, Swords, ArrowLeftRight, Package, RefreshCw, Search 
} from 'lucide-react';
import api from '../services/api';
import StatCard from '../components/common/StatCard';
import StarRating from '../components/common/StarRating';

const COMPARATOR_CATEGORIES = [
  'Smartphones & Mobiles',
  'Laptops & Notebooks',
  'Headphones & Earbuds',
  'Hard Disks & Storage',
  'Home Audio & Speakers',
  'Cameras & Photography',
  'Smart Home & Devices',
  'Cables & Power Accessories',
];

const CATEGORY_DEFAULT_MATCHUPS = {
  'Smartphones & Mobiles': {
    presets: [
      { label: 'iPhone 8 Plus vs Galaxy S20 FE', idA: 'B089SRK8VQ', idB: 'B09PPWVQSB' },
      { label: 'Galaxy S21 Ultra vs Pixel 7 Pro', idA: 'B0B8PDLMMS', idB: 'B0BFCL244S' },
      { label: 'iPhone 12 Mini vs Redmi Note 8', idA: 'B08PP9FM9N', idB: 'B07ZL18B89' },
    ],
    defaultA: 'B089SRK8VQ',
    defaultB: 'B09PPWVQSB',
  },
  'Laptops & Notebooks': {
    presets: [
      { label: 'MacBook Air M2 vs ThinkPad T480', idA: 'B0BB8BHKB8', idB: 'B086DXJ8CC' },
      { label: 'ThinkPad T480 vs Surface Laptop 3', idA: 'B086DXJ8CC', idB: 'B08DC72FBT' },
      { label: 'Toshiba Tecra vs ThinkPad T480', idA: 'B07Q1XBJQ3', idB: 'B086DXJ8CC' },
    ],
    defaultA: 'B0BB8BHKB8',
    defaultB: 'B086DXJ8CC',
  },
  'Headphones & Earbuds': {
    presets: [
      { label: 'Bose QC35 II vs Beats Studio3', idA: 'B09KQC7Z4S', idB: 'B0C38XWF4T' },
      { label: 'Sony MDR7506 vs Bose QC35 II', idA: 'B07CQMZVZ6', idB: 'B09KQC7Z4S' },
      { label: 'Beats Studio3 vs Sony MDR7506', idA: 'B0C38XWF4T', idB: 'B07CQMZVZ6' },
    ],
    defaultA: 'B09KQC7Z4S',
    defaultB: 'B0C38XWF4T',
  },
  'Hard Disks & Storage': {
    presets: [
      { label: 'Kingston A400 SSD vs Crucial BX500', idA: 'B08CKZ36N7', idB: 'B094KDXPDJ' },
      { label: 'Crucial BX500 vs Samsung EVO Select', idA: 'B094KDXPDJ', idB: 'B071R715MZ' },
    ],
    defaultA: 'B08CKZ36N7',
    defaultB: 'B094KDXPDJ',
  },
  'Home Audio & Speakers': {
    presets: [
      { label: 'JBL Flip 4 vs JBL Flip 5', idA: 'B099V8GPR4', idB: 'B09MMWM2Y8' },
      { label: 'JBL Flip 5 vs Bose SoundLink Micro', idA: 'B09MMWM2Y8', idB: 'B09WWG19YS' },
    ],
    defaultA: 'B099V8GPR4',
    defaultB: 'B09MMWM2Y8',
  },
  'Cameras & Photography': {
    presets: [
      { label: 'Nikon 50mm Lens vs Nikon Z 6II', idA: 'B00V8VMXFU', idB: 'B0BQ1W58J9' },
    ],
    defaultA: 'B00V8VMXFU',
    defaultB: 'B0BQ1W58J9',
  },
  'Smart Home & Devices': {
    presets: [
      { label: 'Fire TV Stick Lite vs Fire TV Stick 4K', idA: 'B08F9ZCTCL', idB: 'B0C3NMZ2C7' },
      { label: 'Fire TV Stick 4K vs Echo Dot 3rd Gen', idA: 'B0C3NMZ2C7', idB: 'B07PGL2N7J' },
    ],
    defaultA: 'B08F9ZCTCL',
    defaultB: 'B0C3NMZ2C7',
  },
  'Cables & Power Accessories': {
    presets: [
      { label: 'GE 3-Outlet vs GE 6-Outlet Surge', idA: 'B0BXZ4D1C2', idB: 'B09XYMSZLL' },
      { label: 'Apple Lightning vs GE Surge Protector', idA: 'B09F6T4TGC', idB: 'B0BXZ4D1C2' },
    ],
    defaultA: 'B0BXZ4D1C2',
    defaultB: 'B09XYMSZLL',
  },
};

function SearchableProductSelector({
  label,
  accentColor,
  accentBadge,
  selectedId,
  onSelect,
  products,
  loading,
  searchQuery,
  onSearchChange,
  placeholder,
}) {
  const filtered = products.filter((p) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase().trim();
    const nameMatch = (p.product_name || '').toLowerCase().includes(q);
    const brandMatch = (p.brand || '').toLowerCase().includes(q);
    return nameMatch || brandMatch;
  });

  const selectedProduct = products.find((p) => p.product_id === selectedId) || null;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      padding: '16px',
      borderRadius: 'var(--radius-sm)',
      backgroundColor: 'var(--bg-card)',
      border: '1.5px solid var(--border-medium)',
      boxShadow: 'var(--shadow-sm)',
    }}>
      {/* Label Row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <label style={{ fontSize: '0.84rem', fontWeight: 700, color: accentColor, margin: 0 }}>
          {label}
        </label>
        <span className="badge" style={{ fontSize: '0.68rem', backgroundColor: 'var(--bg-primary)', color: accentColor, border: `1px solid ${accentColor}` }}>
          {accentBadge}
        </span>
      </div>

      {/* 1. Search Bar */}
      <div style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        backgroundColor: 'var(--bg-primary)',
        border: '1px solid var(--border-medium)',
        borderRadius: 'var(--radius-full)',
        padding: '6px 12px',
      }}>
        <Search size={14} color="var(--text-muted)" style={{ marginRight: '8px', flexShrink: 0 }} />
        <input
          type="text"
          placeholder={placeholder || "Search model or brand (e.g. iPhone, Galaxy, ThinkPad)..."}
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          style={{
            width: '100%',
            border: 'none',
            outline: 'none',
            backgroundColor: 'transparent',
            fontSize: '0.82rem',
            color: 'var(--text-primary)',
          }}
        />
        {searchQuery && (
          <button
            type="button"
            onClick={() => onSearchChange('')}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '2px 6px',
              fontSize: '0.85rem',
            }}
            title="Clear search"
          >
            ×
          </button>
        )}
      </div>

      {/* 2. Dropdown Select */}
      <div style={{ position: 'relative' }}>
        <select
          value={selectedId}
          onChange={(e) => onSelect(e.target.value)}
          disabled={loading || filtered.length === 0}
          style={{
            width: '100%',
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            border: '1.5px solid var(--border-medium)',
            backgroundColor: 'var(--bg-primary)',
            fontSize: '0.84rem',
            color: 'var(--text-primary)',
            outline: 'none',
            cursor: filtered.length > 0 ? 'pointer' : 'not-allowed',
          }}
        >
          {filtered.length === 0 ? (
            <option value="">No models match "{searchQuery}"</option>
          ) : (
            filtered.map((p) => (
              <option key={p.product_id} value={p.product_id}>
                [{p.brand}] {p.product_name.slice(0, 52)} ({p.honest_rating || p.average_rating}★ {p.price ? `• $${p.price.toFixed(0)}` : ''})
              </option>
            ))
          )}
        </select>
        {searchQuery && (
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: 'right' }}>
            {filtered.length} {filtered.length === 1 ? 'model' : 'models'} available in search
          </div>
        )}
      </div>

      {/* 3. Selected Model Preview */}
      {selectedProduct && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '8px 12px',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: 'rgba(0, 0, 0, 0.02)',
          border: '1px dashed var(--border-medium)',
        }}>
          {selectedProduct.image_url ? (
            <img
              src={selectedProduct.image_url}
              alt=""
              style={{ width: '38px', height: '38px', objectFit: 'contain', borderRadius: '4px', backgroundColor: '#FFF', flexShrink: 0 }}
            />
          ) : (
            <div style={{ width: '38px', height: '38px', borderRadius: '4px', backgroundColor: '#F0EFEA', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Package size={18} color="var(--text-muted)" />
            </div>
          )}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {selectedProduct.product_name}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Brand: <strong>{selectedProduct.brand}</strong> • Honest: <strong style={{ color: 'var(--accent-terracotta)' }}>{selectedProduct.honest_rating || selectedProduct.average_rating}★</strong> {selectedProduct.price ? `• $${selectedProduct.price.toFixed(2)}` : ''}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ReviewAnalytics() {
  const [overview, setOverview] = useState(null);
  const [hubData, setHubData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Active Category in Category Intelligence Deep Dive
  const [activeCategoryIndex, setActiveCategoryIndex] = useState(0);

  // Interactive Head-to-Head Comparator State
  const [comparatorCategory, setComparatorCategory] = useState('Smartphones & Mobiles');
  const [categoryProducts, setCategoryProducts] = useState([]);
  const [selectedProductA, setSelectedProductA] = useState('B089SRK8VQ');
  const [selectedProductB, setSelectedProductB] = useState('B09PPWVQSB');
  const [searchQueryA, setSearchQueryA] = useState('');
  const [searchQueryB, setSearchQueryB] = useState('');
  const [activeDuel, setActiveDuel] = useState(null);
  const [activeRatingTier, setActiveRatingTier] = useState('5_star');
  const [comparingLoading, setComparingLoading] = useState(false);
  const [categoryLoading, setCategoryLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    Promise.allSettled([
      api.getDashboardOverview(),
      api.getAnalyticsHub(),
    ])
      .then(([ovRes, hubRes]) => {
        if (!isMounted) return;
        if (ovRes.status === 'fulfilled' && ovRes.value) {
          setOverview(ovRes.value);
        }
        if (hubRes.status === 'fulfilled' && hubRes.value) {
          setHubData(hubRes.value);
        }
        setLoading(false);
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to load intelligence analytics');
          setLoading(false);
        }
      });

    return () => { isMounted = false; };
  }, []);

  // Fetch category products for comparator whenever comparatorCategory changes
  useEffect(() => {
    let isMounted = true;
    setCategoryLoading(true);
    setSearchQueryA('');
    setSearchQueryB('');

    api.getCategoryProducts(comparatorCategory, 80)
      .then((prods) => {
        if (!isMounted) return;
        setCategoryProducts(prods || []);
        setCategoryLoading(false);

        const config = CATEGORY_DEFAULT_MATCHUPS[comparatorCategory];
        if (config) {
          setSelectedProductA(config.defaultA);
          setSelectedProductB(config.defaultB);
        } else if (prods && prods.length >= 2) {
          setSelectedProductA(prods[0].product_id);
          setSelectedProductB(prods[1].product_id);
        }
      })
      .catch((err) => {
        console.error('Failed to load category products for comparator:', err);
        if (isMounted) setCategoryLoading(false);
      });

    return () => { isMounted = false; };
  }, [comparatorCategory]);

  // Fetch comparison whenever selectedProductA or selectedProductB changes
  useEffect(() => {
    if (!selectedProductA || !selectedProductB) return;
    let isMounted = true;
    setComparingLoading(true);

    api.compareProducts(selectedProductA, selectedProductB)
      .then((comparison) => {
        if (isMounted) {
          setActiveDuel(comparison);
          setComparingLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to compare products:', err);
        if (isMounted) setComparingLoading(false);
      });

    return () => { isMounted = false; };
  }, [selectedProductA, selectedProductB]);

  const handleSwapProducts = () => {
    setSelectedProductA(selectedProductB);
    setSelectedProductB(selectedProductA);
    const tempQ = searchQueryA;
    setSearchQueryA(searchQueryB);
    setSearchQueryB(tempQ);
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '60px 0' }}>
        <div className="skeleton" style={{ height: '140px', marginBottom: '24px' }} />
        <div className="skeleton" style={{ height: '420px', marginBottom: '24px' }} />
        <div className="skeleton" style={{ height: '320px' }} />
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="container" style={{ padding: '80px 0', textAlign: 'center' }}>
        <div className="card" style={{ maxWidth: '500px', margin: '0 auto', padding: '40px' }}>
          <h2 style={{ fontSize: '1.6rem', color: 'var(--accent-terracotta)', marginBottom: '12px' }}>
            Analytics Unavailable
          </h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            {error || 'Could not load platform analytics from backend.'}
          </p>
        </div>
      </div>
    );
  }

  // Active Category Data
  const categories = hubData?.categories || [];
  const currentCategory = categories[activeCategoryIndex] || categories[0] || null;

  // Chart Formatting
  const ratingData = (overview.rating_distribution || []).map((item) => ({
    stars: `${item.star_rating}★`,
    count: item.count,
    percentage: item.percentage,
  }));

  const verifiedPieData = [
    { name: 'Verified Purchase', value: overview.total_verified_reviews, color: '#87977A' },
    { name: 'Unverified Feedback', value: overview.total_reviews - overview.total_verified_reviews, color: '#D9D2C3' },
  ];

  const getAspectBadge = (scoreA, scoreB) => {
    if (Math.abs(scoreA - scoreB) < 0.05) {
      return { labelA: 'Tie', labelB: 'Tie', colorA: 'var(--text-muted)', colorB: 'var(--text-muted)' };
    }
    if (scoreA > scoreB) {
      return { labelA: 'Winner 🏆', labelB: '', colorA: 'var(--accent-sage-dark)', colorB: '' };
    }
    return { labelA: '', labelB: 'Winner 🏆', colorA: '', colorB: 'var(--accent-sage-dark)' };
  };

  return (
    <div style={{ padding: '40px 0 80px 0' }}>
      <div className="container">
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
            <span className="badge badge-sage">
              <Sparkles size={12} />
              MARKET INTELLIGENCE & COMPARISON HUB
            </span>
          </div>
          <h1 style={{ fontSize: '2.5rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
            Review Intelligence & Market Analytics
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', maxWidth: '780px', lineHeight: 1.5 }}>
            Empirical reliability benchmarks, head-to-head hardware duels, and market failure radar synthesized from {overview.total_reviews.toLocaleString()} verified customer reviews across {overview.total_products.toLocaleString()} catalog products.
          </p>
        </div>

        {/* Global Platform Telemetry Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
          marginBottom: '36px',
        }}>
          <StatCard
            label="Verified Reviews"
            value={overview.total_reviews.toLocaleString()}
            subtext="Cleaned customer reviews"
            icon={Database}
            accent="sage"
          />
          <StatCard
            label="Catalog Electronics"
            value={overview.total_products.toLocaleString()}
            subtext="Across 8 verified categories"
            icon={Layers}
            accent="sage"
          />
          <StatCard
            label="Overall Mean Rating"
            value={`${overview.overall_average_review_rating.toFixed(2)} ★`}
            subtext="Marketplace review consensus"
            icon={Star}
            accent="gold"
          />
          <StatCard
            label="Verified Buyer Ratio"
            value={`${overview.verified_reviews_percentage}%`}
            subtext={`${overview.total_verified_reviews.toLocaleString()} verified orders`}
            icon={ShieldCheck}
            accent="gold"
          />
        </div>

        {/* ========================================================================= */}
        {/* SECTION 1: INTERACTIVE CATEGORY INTELLIGENCE & BENCHMARKS */}
        {/* ========================================================================= */}
        {categories.length > 0 && currentCategory && (
          <div className="card" style={{
            padding: '32px',
            marginBottom: '40px',
            border: '2px solid var(--border-medium)',
            boxShadow: 'var(--shadow-sm)',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '12px',
              marginBottom: '20px',
            }}>
              <div>
                <span className="badge badge-gold" style={{ marginBottom: '6px' }}>
                  CATEGORY DEEP DIVE
                </span>
                <h2 style={{ fontSize: '1.65rem', color: 'var(--text-primary)', margin: 0 }}>
                  Reliability & Aspect Benchmarks
                </h2>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                Select a category below to explore its specific durability and failure rates.
              </p>
            </div>

            {/* Category Switcher Pills */}
            <div style={{
              display: 'flex',
              gap: '8px',
              overflowX: 'auto',
              paddingBottom: '12px',
              marginBottom: '28px',
            }}>
              {categories.map((cat, idx) => {
                const isSelected = idx === activeCategoryIndex;
                return (
                  <button
                    key={cat.category}
                    onClick={() => setActiveCategoryIndex(idx)}
                    style={{
                      padding: '8px 16px',
                      borderRadius: 'var(--radius-full)',
                      fontSize: '0.84rem',
                      fontWeight: isSelected ? 600 : 500,
                      backgroundColor: isSelected ? 'var(--text-primary)' : 'var(--bg-primary)',
                      color: isSelected ? 'var(--bg-primary)' : 'var(--text-secondary)',
                      border: isSelected ? '1px solid var(--text-primary)' : '1px solid var(--border-medium)',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {cat.category}
                  </button>
                );
              })}
            </div>

            {/* Active Category Detail Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              gap: '28px',
              marginBottom: '28px',
            }}>
              {/* Left Column: Dimension Scores */}
              <div style={{
                padding: '24px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-light)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
                  <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', margin: 0 }}>
                    {currentCategory.category} Benchmark
                  </h3>
                  <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--accent-sage-dark)' }}>
                    {currentCategory.satisfaction_rate}% Satisfaction
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  {/* Durability */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-primary)', fontWeight: 600 }}>
                        <Wrench size={14} color="var(--accent-sage-dark)" /> Durability & Build Quality
                      </span>
                      <strong>{currentCategory.durability_score} / 5.0</strong>
                    </div>
                    <div style={{ height: '7px', backgroundColor: 'var(--border-light)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${(currentCategory.durability_score / 5) * 100}%`, height: '100%', backgroundColor: 'var(--accent-sage)' }} />
                    </div>
                  </div>

                  {/* Battery & Life */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-primary)', fontWeight: 600 }}>
                        <Battery size={14} color="var(--accent-gold)" /> Lifespan & Battery Longevity
                      </span>
                      <strong>{currentCategory.battery_score} / 5.0</strong>
                    </div>
                    <div style={{ height: '7px', backgroundColor: 'var(--border-light)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${(currentCategory.battery_score / 5) * 100}%`, height: '100%', backgroundColor: 'var(--accent-gold)' }} />
                    </div>
                  </div>

                  {/* Performance */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-primary)', fontWeight: 600 }}>
                        <Cpu size={14} color="var(--accent-sage)" /> Performance & Speed
                      </span>
                      <strong>{currentCategory.performance_score} / 5.0</strong>
                    </div>
                    <div style={{ height: '7px', backgroundColor: 'var(--border-light)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${(currentCategory.performance_score / 5) * 100}%`, height: '100%', backgroundColor: 'var(--accent-sage)' }} />
                    </div>
                  </div>

                  {/* Value */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-primary)', fontWeight: 600 }}>
                        <Award size={14} color="var(--accent-gold)" /> Value for Money
                      </span>
                      <strong>{currentCategory.value_score} / 5.0</strong>
                    </div>
                    <div style={{ height: '7px', backgroundColor: 'var(--border-light)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${(currentCategory.value_score / 5) * 100}%`, height: '100%', backgroundColor: 'var(--accent-gold)' }} />
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid var(--border-light)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Grounded across {currentCategory.product_count.toLocaleString()} catalog products and customer review sentiments.
                </div>
              </div>

              {/* Right Column: Known Failure Modes & Complaints */}
              <div style={{
                padding: '24px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'rgba(200, 109, 86, 0.05)',
                border: '1px solid rgba(200, 109, 86, 0.25)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                  <AlertTriangle size={18} color="var(--accent-terracotta)" />
                  <h3 style={{ fontSize: '1.15rem', color: 'var(--accent-terracotta)', margin: 0 }}>
                    Top Reported Failure Modes & Consumer Complaints
                  </h3>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  The most prevalent issues cited in 1★ and 2★ reviews for {currentCategory.category}:
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {currentCategory.top_complaints.map((item, i) => (
                    <div key={i}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '3px' }}>
                        <span style={{ color: 'var(--text-primary)' }}>{item.issue}</span>
                        <strong style={{ color: 'var(--accent-terracotta)' }}>{item.percentage}%</strong>
                      </div>
                      <div style={{ height: '6px', backgroundColor: 'rgba(200, 109, 86, 0.15)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${item.percentage}%`, height: '100%', backgroundColor: 'var(--accent-terracotta)' }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Category Products Across All Rating Tiers (5★, 4★, 3★, 1-2★) */}
            {(() => {
              const tierProducts = (currentCategory.tiered_products && currentCategory.tiered_products[activeRatingTier]) || currentCategory.top_products || [];
              const tierMeta = {
                '5_star': {
                  title: `🌟 5★ Category Champions in ${currentCategory.category}`,
                  desc: 'Elite models with top customer satisfaction and low failure rates.',
                  badge: '✓ Elite Champion',
                  badgeBg: '#F0F5ED',
                  badgeColor: '#4A5B42',
                },
                '4_star': {
                  title: `⚡ 4★ Solid Performers in ${currentCategory.category}`,
                  desc: 'Balanced everyday options with solid performance and manageable caveats.',
                  badge: '⚡ High Value',
                  badgeBg: '#FAF5EB',
                  badgeColor: '#8C6C38',
                },
                '3_star': {
                  title: `⚖️ 3★ Mixed / Trade-Off Models in ${currentCategory.category}`,
                  desc: 'Models with noticeable compromises, mixed reviews, and moderate return risk.',
                  badge: '⚖️ Notable Flaws',
                  badgeBg: '#FFF6E6',
                  badgeColor: '#A35D00',
                },
                '1_2_star': {
                  title: `⚠️ 1-2★ Critical Watchlist in ${currentCategory.category}`,
                  desc: 'Low-rated products with verified defect reports and high customer return rates.',
                  badge: '⛔ High Defect Risk',
                  badgeBg: '#FDF2F0',
                  badgeColor: '#B25E46',
                },
              }[activeRatingTier] || {
                title: `Models in ${currentCategory.category}`,
                desc: 'Products featured from authentic verified customer reviews.',
                badge: 'Verified',
                badgeBg: '#F0F5ED',
                badgeColor: '#4A5B42',
              };

              return (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '12px' }}>
                    <div>
                      <h4 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', margin: '0 0 4px 0', fontWeight: 700 }}>
                        {tierMeta.title}
                      </h4>
                      <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', margin: 0 }}>
                        {tierMeta.desc}
                      </p>
                    </div>
                    <Link
                      to={`/products?category=${encodeURIComponent(currentCategory.category)}`}
                      style={{ fontSize: '0.84rem', color: 'var(--accent-sage-dark)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                    >
                      View All in Explorer <ArrowRight size={13} />
                    </Link>
                  </div>

                  {/* Rating Tier Selector Tabs */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    overflowX: 'auto',
                    paddingBottom: '12px',
                    marginBottom: '18px',
                  }}>
                    {[
                      { key: '5_star', label: '🌟 5★ Champions' },
                      { key: '4_star', label: '⚡ 4★ Solid Performers' },
                      { key: '3_star', label: '⚖️ 3★ Mixed / Trade-Off' },
                      { key: '1_2_star', label: '⚠️ 1-2★ Critical Watchlist' },
                    ].map((tab) => {
                      const isSelected = activeRatingTier === tab.key;
                      return (
                        <button
                          key={tab.key}
                          type="button"
                          onClick={() => setActiveRatingTier(tab.key)}
                          style={{
                            padding: '6px 14px',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '0.82rem',
                            fontWeight: isSelected ? 600 : 500,
                            backgroundColor: isSelected ? 'var(--text-primary)' : 'var(--bg-card)',
                            color: isSelected ? 'var(--bg-primary)' : 'var(--text-secondary)',
                            border: isSelected ? '1px solid var(--text-primary)' : '1px solid var(--border-light)',
                            cursor: 'pointer',
                            whiteSpace: 'nowrap',
                            transition: 'all 0.15s ease',
                          }}
                        >
                          {tab.label}
                        </button>
                      );
                    })}
                  </div>

                  {/* Product Cards Grid */}
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                    gap: '16px',
                  }}>
                    {tierProducts.map((prod) => (
                      <div
                        key={prod.product_id}
                        style={{
                          padding: '18px',
                          borderRadius: 'var(--radius-sm)',
                          backgroundColor: 'var(--bg-primary)',
                          border: '1px solid var(--border-light)',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'space-between',
                          boxShadow: 'var(--shadow-sm)',
                        }}
                      >
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <span className="badge badge-sage" style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
                              {prod.brand || 'Electronics'}
                            </span>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span style={{
                                fontFamily: 'var(--font-serif)',
                                fontSize: '1.1rem',
                                fontWeight: 700,
                                color: 'var(--text-primary)',
                              }}>
                                {prod.honest_rating ? `${prod.honest_rating.toFixed(1)}★` : `${prod.average_rating.toFixed(1)}★`}
                              </span>
                              <span style={{
                                fontSize: '0.65rem',
                                color: tierMeta.badgeColor,
                                backgroundColor: tierMeta.badgeBg,
                                padding: '2px 6px',
                                borderRadius: 'var(--radius-full)',
                                fontWeight: 600,
                              }}>
                                {tierMeta.badge}
                              </span>
                            </div>
                          </div>

                          <Link to={`/products/${prod.product_id}`}>
                            <h5 style={{
                              fontSize: '0.92rem',
                              color: 'var(--text-primary)',
                              lineHeight: 1.4,
                              marginBottom: '8px',
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                              fontWeight: 600,
                              cursor: 'pointer',
                            }}>
                              {prod.product_name}
                            </h5>
                          </Link>

                          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                            Market Listed: {prod.average_rating.toFixed(1)}★ • {prod.rating_number ? prod.rating_number.toLocaleString() : 0} ratings
                          </div>
                        </div>

                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          paddingTop: '12px',
                          borderTop: '1px solid var(--border-light)',
                          marginTop: '10px',
                        }}>
                          <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                            {prod.price ? `$${prod.price.toFixed(2)}` : 'Listing Unavailable'}
                          </span>
                          <Link
                            to={`/products/${prod.product_id}`}
                            className="btn btn-primary"
                            style={{ padding: '6px 12px', fontSize: '0.76rem', borderRadius: 'var(--radius-full)' }}
                          >
                            View Report ↗
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* ========================================================================= */}
        {/* SECTION 2: INTERACTIVE HEAD-TO-HEAD PRODUCT COMPARATOR */}
        {/* ========================================================================= */}
        <div className="card" style={{
          padding: '36px',
          marginBottom: '40px',
          backgroundColor: 'var(--bg-card)',
          border: '2px solid var(--border-medium)',
          boxShadow: 'var(--shadow-md)',
        }}>
          {/* Header */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <span className="badge badge-sage">
                <Swords size={12} />
                CUSTOM HARDWARE COMPARATOR
              </span>
            </div>
            <h2 style={{ fontSize: '1.8rem', color: 'var(--text-primary)', margin: '0 0 6px 0' }}>
              Interactive Head-to-Head Product Comparator
            </h2>
            <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', margin: 0, maxWidth: '820px', lineHeight: 1.55 }}>
              Choose any category and select any two products of your choice to run an empirical side-by-side reliability, battery life, performance, and honest rating comparison.
            </p>
          </div>

          {/* Step 1: Category Selector */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.5px', marginBottom: '10px' }}>
              Step 1: Choose Comparison Category
            </div>
            <div style={{
              display: 'flex',
              gap: '8px',
              overflowX: 'auto',
              paddingBottom: '8px',
            }}>
              {COMPARATOR_CATEGORIES.map((cat) => {
                const isSelected = cat === comparatorCategory;
                return (
                  <button
                    key={cat}
                    onClick={() => setComparatorCategory(cat)}
                    style={{
                      padding: '7px 14px',
                      borderRadius: 'var(--radius-full)',
                      fontSize: '0.82rem',
                      fontWeight: isSelected ? 600 : 500,
                      backgroundColor: isSelected ? 'var(--text-primary)' : 'var(--bg-primary)',
                      color: isSelected ? 'var(--bg-primary)' : 'var(--text-secondary)',
                      border: isSelected ? '1px solid var(--text-primary)' : '1px solid var(--border-medium)',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Step 2: Interactive Product Selection Box */}
          <div style={{
            padding: '22px 24px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--bg-primary)',
            border: '1px solid var(--border-medium)',
            marginBottom: '28px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.5px' }}>
                Step 2: Choose Any Two Products in {comparatorCategory}
              </div>
              {categoryLoading && (
                <span style={{ fontSize: '0.78rem', color: 'var(--accent-sage-dark)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <RefreshCw size={12} className="spin" /> Loading models...
                </span>
              )}
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '16px',
              alignItems: 'center',
            }}>
              {/* Product A Selector with Search Bar + Dropdown */}
              <SearchableProductSelector
                label="Challenger 1 (Product A)"
                accentColor="var(--accent-sage-dark)"
                accentBadge="Challenger A"
                selectedId={selectedProductA}
                onSelect={setSelectedProductA}
                products={categoryProducts}
                loading={categoryLoading}
                searchQuery={searchQueryA}
                onSearchChange={setSearchQueryA}
                placeholder="Search Challenger 1 (e.g. iPhone, S20)..."
              />

              {/* Swap Button (Desktop & Mobile) */}
              <div style={{ textAlign: 'center', margin: '4px 0' }}>
                <button
                  type="button"
                  onClick={handleSwapProducts}
                  className="btn btn-outline"
                  title="Swap Challengers"
                  style={{
                    padding: '9px 18px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.82rem',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    whiteSpace: 'nowrap',
                  }}
                >
                  <ArrowLeftRight size={14} />
                  Swap ⇄
                </button>
              </div>

              {/* Product B Selector with Search Bar + Dropdown */}
              <SearchableProductSelector
                label="Challenger 2 (Product B)"
                accentColor="var(--accent-gold-dark)"
                accentBadge="Challenger B"
                selectedId={selectedProductB}
                onSelect={setSelectedProductB}
                products={categoryProducts}
                loading={categoryLoading}
                searchQuery={searchQueryB}
                onSearchChange={setSearchQueryB}
                placeholder="Search Challenger 2 (e.g. Galaxy, Pixel)..."
              />
            </div>

            {/* Quick Matchup Presets for Current Category */}
            {CATEGORY_DEFAULT_MATCHUPS[comparatorCategory]?.presets && (
              <div style={{
                marginTop: '16px',
                paddingTop: '12px',
                borderTop: '1px solid var(--border-light)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                flexWrap: 'wrap',
              }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                  Popular Matchups:
                </span>
                {CATEGORY_DEFAULT_MATCHUPS[comparatorCategory].presets.map((preset, idx) => {
                  const isActive = selectedProductA === preset.idA && selectedProductB === preset.idB;
                  return (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        setSelectedProductA(preset.idA);
                        setSelectedProductB(preset.idB);
                      }}
                      style={{
                        padding: '4px 12px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: isActive ? 'var(--text-primary)' : 'var(--bg-card)',
                        color: isActive ? 'var(--bg-primary)' : 'var(--text-primary)',
                        border: isActive ? '1px solid var(--text-primary)' : '1px solid var(--border-medium)',
                        fontSize: '0.76rem',
                        fontWeight: isActive ? 600 : 500,
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      ⚡ {preset.label}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Step 3: Comparison Duel Output */}
          {comparingLoading ? (
            <div style={{ padding: '60px 0', textAlign: 'center' }}>
              <div className="skeleton" style={{ height: '320px', borderRadius: 'var(--radius-md)' }} />
            </div>
          ) : activeDuel ? (
            <div style={{
              backgroundColor: 'var(--bg-primary)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-medium)',
              padding: '28px',
            }}>
              {/* Product Headers with VS & Winner Badge */}
              <div className="duel-container" style={{
                marginBottom: '28px',
              }}>
                {/* Product A Header */}
                <div style={{ textAlign: 'left' }}>
                  <span className="badge badge-sage" style={{ marginBottom: '6px' }}>
                    {activeDuel.product_a.brand}
                  </span>
                  <Link to={`/products/${activeDuel.product_a.product_id}`}>
                    <h3 style={{
                      fontSize: '1.2rem',
                      color: 'var(--text-primary)',
                      marginBottom: '8px',
                      lineHeight: 1.35,
                      cursor: 'pointer',
                    }}>
                      {activeDuel.product_a.product_name}
                    </h3>
                  </Link>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1.7rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {activeDuel.product_a.overall_rating.toFixed(2)} ★
                    </span>
                    <span style={{
                      fontSize: '0.7rem',
                      color: '#B25E46',
                      backgroundColor: '#FDF2F0',
                      padding: '2px 6px',
                      borderRadius: 'var(--radius-full)',
                      fontWeight: 600,
                    }}>
                      Honest Score
                    </span>
                    <span className="badge badge-neutral" style={{ fontSize: '0.74rem' }}>
                      Grade {activeDuel.product_a.quality_grade}
                    </span>
                    {activeDuel.product_a.price && (
                      <span style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--accent-sage-dark)' }}>
                        ${activeDuel.product_a.price.toFixed(2)}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Amazon Listed: {activeDuel.product_a.marketplace_listed_rating ? `${activeDuel.product_a.marketplace_listed_rating.toFixed(1)}★` : '4.2★'}
                  </div>
                </div>

                {/* Center VS & Leader Badge */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <div style={{
                    width: '54px',
                    height: '54px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--text-primary)',
                    color: 'var(--bg-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 800,
                    fontSize: '1rem',
                    letterSpacing: '1px',
                    boxShadow: 'var(--shadow-sm)',
                    flexShrink: 0,
                  }}>
                    VS
                  </div>
                  {(() => {
                    const diff = activeDuel.product_a.overall_rating - activeDuel.product_b.overall_rating;
                    if (diff > 0.15) {
                      return (
                        <span style={{
                          fontSize: '0.72rem',
                          padding: '3px 8px',
                          borderRadius: 'var(--radius-full)',
                          backgroundColor: 'var(--bg-sage-subtle)',
                          color: 'var(--accent-sage-dark)',
                          fontWeight: 700,
                          whiteSpace: 'nowrap',
                        }}>
                          🏆 {activeDuel.product_a.brand} Leads
                        </span>
                      );
                    }
                    if (diff < -0.15) {
                      return (
                        <span style={{
                          fontSize: '0.72rem',
                          padding: '3px 8px',
                          borderRadius: 'var(--radius-full)',
                          backgroundColor: '#FDF8EC',
                          color: '#976F1D',
                          fontWeight: 700,
                          whiteSpace: 'nowrap',
                        }}>
                          🏆 {activeDuel.product_b.brand} Leads
                        </span>
                      );
                    }
                    return (
                      <span style={{
                        fontSize: '0.72rem',
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: 'var(--bg-card)',
                        color: 'var(--text-secondary)',
                        fontWeight: 600,
                        whiteSpace: 'nowrap',
                      }}>
                        ⚖️ Evenly Matched
                      </span>
                    );
                  })()}
                </div>

                {/* Product B Header */}
                <div style={{ textAlign: 'right' }}>
                  <span className="badge badge-gold" style={{ marginBottom: '6px' }}>
                    {activeDuel.product_b.brand}
                  </span>
                  <Link to={`/products/${activeDuel.product_b.product_id}`}>
                    <h3 style={{
                      fontSize: '1.2rem',
                      color: 'var(--text-primary)',
                      marginBottom: '8px',
                      lineHeight: 1.35,
                      cursor: 'pointer',
                    }}>
                      {activeDuel.product_b.product_name}
                    </h3>
                  </Link>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
                    {activeDuel.product_b.price && (
                      <span style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--accent-sage-dark)' }}>
                        ${activeDuel.product_b.price.toFixed(2)}
                      </span>
                    )}
                    <span className="badge badge-neutral" style={{ fontSize: '0.74rem' }}>
                      Grade {activeDuel.product_b.quality_grade}
                    </span>
                    <span style={{
                      fontSize: '0.7rem',
                      color: '#B25E46',
                      backgroundColor: '#FDF2F0',
                      padding: '2px 6px',
                      borderRadius: 'var(--radius-full)',
                      fontWeight: 600,
                    }}>
                      Honest Score
                    </span>
                    <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1.7rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {activeDuel.product_b.overall_rating.toFixed(2)} ★
                    </span>
                  </div>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Amazon Listed: {activeDuel.product_b.marketplace_listed_rating ? `${activeDuel.product_b.marketplace_listed_rating.toFixed(1)}★` : '4.2★'}
                  </div>
                </div>
              </div>

              {/* Aspect Comparison Bars */}
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                padding: '20px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-light)',
                marginBottom: '24px',
              }}>
                {/* Durability */}
                {(() => {
                  const badge = getAspectBadge(activeDuel.product_a.durability, activeDuel.product_b.durability);
                  return (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px', fontSize: '0.86rem' }}>
                        <span style={{ fontWeight: 600, color: badge.colorA }}>
                          {activeDuel.product_a.durability.toFixed(2)} / 5.0 {badge.labelA}
                        </span>
                        <strong style={{ color: 'var(--text-primary)' }}>Durability & Build Quality</strong>
                        <span style={{ fontWeight: 600, color: badge.colorB }}>
                          {badge.labelB} {activeDuel.product_b.durability.toFixed(2)} / 5.0
                        </span>
                      </div>
                      <div style={{ display: 'flex', height: '8px', gap: '4px', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ flex: 1, backgroundColor: 'var(--border-light)', display: 'flex', justifyContent: 'flex-end' }}>
                          <div style={{ width: `${(activeDuel.product_a.durability / 5) * 100}%`, backgroundColor: 'var(--accent-sage)' }} />
                        </div>
                        <div style={{ flex: 1, backgroundColor: 'var(--border-light)' }}>
                          <div style={{ width: `${(activeDuel.product_b.durability / 5) * 100}%`, backgroundColor: 'var(--accent-gold)' }} />
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* Battery / Lifespan */}
                {(() => {
                  const badge = getAspectBadge(activeDuel.product_a.battery, activeDuel.product_b.battery);
                  return (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px', fontSize: '0.86rem' }}>
                        <span style={{ fontWeight: 600, color: badge.colorA }}>
                          {activeDuel.product_a.battery.toFixed(2)} / 5.0 {badge.labelA}
                        </span>
                        <strong style={{ color: 'var(--text-primary)' }}>Lifespan & Battery Longevity</strong>
                        <span style={{ fontWeight: 600, color: badge.colorB }}>
                          {badge.labelB} {activeDuel.product_b.battery.toFixed(2)} / 5.0
                        </span>
                      </div>
                      <div style={{ display: 'flex', height: '8px', gap: '4px', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ flex: 1, backgroundColor: 'var(--border-light)', display: 'flex', justifyContent: 'flex-end' }}>
                          <div style={{ width: `${(activeDuel.product_a.battery / 5) * 100}%`, backgroundColor: 'var(--accent-sage)' }} />
                        </div>
                        <div style={{ flex: 1, backgroundColor: 'var(--border-light)' }}>
                          <div style={{ width: `${(activeDuel.product_b.battery / 5) * 100}%`, backgroundColor: 'var(--accent-gold)' }} />
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* Performance */}
                {(() => {
                  const badge = getAspectBadge(activeDuel.product_a.performance, activeDuel.product_b.performance);
                  return (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px', fontSize: '0.86rem' }}>
                        <span style={{ fontWeight: 600, color: badge.colorA }}>
                          {activeDuel.product_a.performance.toFixed(2)} / 5.0 {badge.labelA}
                        </span>
                        <strong style={{ color: 'var(--text-primary)' }}>Performance & Speed</strong>
                        <span style={{ fontWeight: 600, color: badge.colorB }}>
                          {badge.labelB} {activeDuel.product_b.performance.toFixed(2)} / 5.0
                        </span>
                      </div>
                      <div style={{ display: 'flex', height: '8px', gap: '4px', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ flex: 1, backgroundColor: 'var(--border-light)', display: 'flex', justifyContent: 'flex-end' }}>
                          <div style={{ width: `${(activeDuel.product_a.performance / 5) * 100}%`, backgroundColor: 'var(--accent-sage)' }} />
                        </div>
                        <div style={{ flex: 1, backgroundColor: 'var(--border-light)' }}>
                          <div style={{ width: `${(activeDuel.product_b.performance / 5) * 100}%`, backgroundColor: 'var(--accent-gold)' }} />
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* Value */}
                {(() => {
                  const badge = getAspectBadge(activeDuel.product_a.value, activeDuel.product_b.value);
                  return (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px', fontSize: '0.86rem' }}>
                        <span style={{ fontWeight: 600, color: badge.colorA }}>
                          {activeDuel.product_a.value.toFixed(2)} / 5.0 {badge.labelA}
                        </span>
                        <strong style={{ color: 'var(--text-primary)' }}>Value for Money</strong>
                        <span style={{ fontWeight: 600, color: badge.colorB }}>
                          {badge.labelB} {activeDuel.product_b.value.toFixed(2)} / 5.0
                        </span>
                      </div>
                      <div style={{ display: 'flex', height: '8px', gap: '4px', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ flex: 1, backgroundColor: 'var(--border-light)', display: 'flex', justifyContent: 'flex-end' }}>
                          <div style={{ width: `${(activeDuel.product_a.value / 5) * 100}%`, backgroundColor: 'var(--accent-sage)' }} />
                        </div>
                        <div style={{ flex: 1, backgroundColor: 'var(--border-light)' }}>
                          <div style={{ width: `${(activeDuel.product_b.value / 5) * 100}%`, backgroundColor: 'var(--accent-gold)' }} />
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>

              {/* Strengths & Known Flaws Side-by-Side Comparison */}
              {(activeDuel.product_a.strengths || activeDuel.product_b.strengths) && (
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: '20px',
                  marginBottom: '24px',
                }}>
                  {/* Challenger A Strengths & Flaws */}
                  <div style={{
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-light)',
                  }}>
                    <strong style={{ display: 'block', fontSize: '0.86rem', color: 'var(--accent-sage-dark)', marginBottom: '8px' }}>
                      ✓ {activeDuel.product_a.brand} Key Strengths:
                    </strong>
                    <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 12px 0', fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {(activeDuel.product_a.strengths || []).slice(0, 2).map((s, idx) => (
                        <li key={idx} style={{ display: 'flex', gap: '6px' }}><span>•</span> <span>{s}</span></li>
                      ))}
                    </ul>
                    <strong style={{ display: 'block', fontSize: '0.86rem', color: 'var(--accent-terracotta)', marginBottom: '8px' }}>
                      ⚠ Watch-Outs:
                    </strong>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {(activeDuel.product_a.flaws || []).slice(0, 2).map((f, idx) => (
                        <li key={idx} style={{ display: 'flex', gap: '6px' }}><span>•</span> <span>{f}</span></li>
                      ))}
                    </ul>
                  </div>

                  {/* Challenger B Strengths & Flaws */}
                  <div style={{
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-light)',
                  }}>
                    <strong style={{ display: 'block', fontSize: '0.86rem', color: 'var(--accent-gold-dark)', marginBottom: '8px' }}>
                      ✓ {activeDuel.product_b.brand} Key Strengths:
                    </strong>
                    <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 12px 0', fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {(activeDuel.product_b.strengths || []).slice(0, 2).map((s, idx) => (
                        <li key={idx} style={{ display: 'flex', gap: '6px' }}><span>•</span> <span>{s}</span></li>
                      ))}
                    </ul>
                    <strong style={{ display: 'block', fontSize: '0.86rem', color: 'var(--accent-terracotta)', marginBottom: '8px' }}>
                      ⚠ Watch-Outs:
                    </strong>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {(activeDuel.product_b.flaws || []).slice(0, 2).map((f, idx) => (
                        <li key={idx} style={{ display: 'flex', gap: '6px' }}><span>•</span> <span>{f}</span></li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Synthesized Duel Verdict */}
              <div style={{
                padding: '16px 20px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-medium)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '14px',
              }}>
                <div style={{ flex: 1, fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.55 }}>
                  💡 <span style={{ fontWeight: 700 }}>Executive Matchup Verdict:</span> {activeDuel.winner_summary}
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <Link
                    to={`/products/${activeDuel.product_a.product_id}`}
                    className="btn btn-outline"
                    style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                  >
                    {activeDuel.product_a.brand} Report ↗
                  </Link>
                  <Link
                    to={`/products/${activeDuel.product_b.product_id}`}
                    className="btn btn-outline"
                    style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                  >
                    {activeDuel.product_b.brand} Report ↗
                  </Link>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
              Select two products above to generate a comparison duel.
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* SECTION 3: MARKET RELIABILITY & FAILURE RADAR */}
        {/* ========================================================================= */}
        {hubData?.market_flaws && (
          <div className="card" style={{ padding: '32px', marginBottom: '40px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="badge badge-sage">MARKET-WIDE RADAR</span>
            </div>
            <h2 style={{ fontSize: '1.6rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
              Why Do Consumers Return or Criticize Electronics?
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '24px', maxWidth: '720px' }}>
              Across thousands of critical 1-star and 2-star consumer reviews, we analyzed the root cause failure modes that trigger buyer dissatisfaction:
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {hubData.market_flaws.map((flaw, i) => (
                <div
                  key={i}
                  style={{
                    padding: '20px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-primary)',
                    border: '1px solid var(--border-light)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <strong style={{ fontSize: '0.94rem', color: 'var(--text-primary)' }}>
                        {flaw.category}
                      </strong>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.78rem',
                        fontWeight: 700,
                        backgroundColor: 'rgba(200, 109, 86, 0.1)',
                        color: 'var(--accent-terracotta)',
                      }}>
                        {flaw.failure_percentage}% of flaws
                      </span>
                    </div>

                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                      {flaw.description}
                    </p>
                  </div>

                  <div style={{ marginTop: '12px', height: '6px', backgroundColor: 'var(--border-light)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${flaw.failure_percentage * 2.5}%`, height: '100%', backgroundColor: 'var(--accent-terracotta)' }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* SECTION 4: GLOBAL RATING & VERIFICATION INTEGRITY (MACRO REFERENCE) */}
        {/* ========================================================================= */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '24px',
        }}>
          {/* Chart 1: Global Star Rating Distribution */}
          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '4px' }}>
              Platform Rating Distribution
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '18px' }}>
              Frequency of star ratings across all collected customer feedback.
            </p>

            <div style={{ height: '240px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={ratingData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <XAxis dataKey="stars" tick={{ fill: '#585D50', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#585D50', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      borderRadius: '8px',
                      border: '1px solid #E7E2D5',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.06)',
                    }}
                    formatter={(val, name, item) => [`${val.toLocaleString()} reviews (${item.payload.percentage}%)`, 'Volume']}
                  />
                  <Bar dataKey="count" fill="var(--accent-sage)" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Chart 2: Verified Purchase Ratio Donut */}
          <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '4px' }}>
              Purchase Verification Integrity
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '18px' }}>
              Proportion of reviews originating from Amazon verified purchasers.
            </p>

            <div style={{ height: '240px', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={verifiedPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {verifiedPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      borderRadius: '8px',
                      border: '1px solid #E7E2D5',
                    }}
                    formatter={(val) => [`${val.toLocaleString()} reviews`, 'Count']}
                  />
                  <Legend
                    verticalAlign="bottom"
                    iconType="circle"
                    formatter={(val) => <span style={{ color: '#252820', fontSize: '0.85rem' }}>{val}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
