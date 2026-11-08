import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  Search, Filter, SlidersHorizontal, ChevronLeft, ChevronRight, 
  RotateCcw, Smartphone, Laptop, Camera, Headphones, Layers, 
  Watch, Check, Info, Sparkles, HardDrive, Volume2, Tv, Plug 
} from 'lucide-react';
import api from '../services/api';
import ProductCard from '../components/common/ProductCard';

export default function ProductExplorer() {
  const [searchParams, setSearchParams] = useSearchParams();

  // URL state sync
  const queryParam = searchParams.get('q') || '';
  const categoryParam = searchParams.get('category') || '';
  const brandParam = searchParams.get('brand') || '';
  const pageParam = parseInt(searchParams.get('page') || '1', 10);
  const sortByParam = searchParams.get('sort_by') || 'rating_number';
  const orderParam = searchParams.get('order') || 'desc';
  const minRatingParam = searchParams.get('min_rating') || '';
  const maxRatingParam = searchParams.get('max_rating') || '';

  // Local state
  const [searchInput, setSearchInput] = useState(queryParam);
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Sync searchInput when queryParam changes
  useEffect(() => {
    setSearchInput(queryParam);
  }, [queryParam]);

  // Fetch products whenever search params change
  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    const fetchPromise = api.getProducts({
      page: pageParam,
      page_size: 20,
      q: queryParam.trim() || undefined,
      category: categoryParam || undefined,
      brand: brandParam || undefined,
      min_rating: minRatingParam ? parseFloat(minRatingParam) : undefined,
      max_rating: maxRatingParam ? parseFloat(maxRatingParam) : undefined,
      sort_by: sortByParam,
      order: orderParam,
    });

    fetchPromise
      .then((data) => {
        if (isMounted) {
          setProducts(data.items || []);
          setTotal(data.total || 0);
          setTotalPages(data.total_pages || 1);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to fetch products');
          setLoading(false);
        }
      });

    return () => { isMounted = false; };
  }, [queryParam, categoryParam, brandParam, pageParam, sortByParam, orderParam, minRatingParam, maxRatingParam]);

  const updateParam = (key, value) => {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    // Reset page to 1 whenever a filter changes
    if (key !== 'page') {
      next.set('page', '1');
    }
    setSearchParams(next);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    updateParam('q', searchInput.trim());
  };

  const handleResetFilters = () => {
    setSearchInput('');
    setSearchParams(new URLSearchParams());
  };

  const getRatingSelectValue = () => {
    if (minRatingParam === '4.5' && !maxRatingParam) return 'tier_5';
    if (minRatingParam === '3.8' && maxRatingParam === '4.4') return 'tier_4';
    if (minRatingParam === '2.8' && maxRatingParam === '3.7') return 'tier_3';
    if (!minRatingParam && maxRatingParam === '2.7') return 'tier_1_2';
    return '';
  };

  const handleRatingSelectChange = (val) => {
    const next = new URLSearchParams(searchParams);
    next.delete('min_rating');
    next.delete('max_rating');
    if (val === 'tier_5') {
      next.set('min_rating', '4.5');
    } else if (val === 'tier_4') {
      next.set('min_rating', '3.8');
      next.set('max_rating', '4.4');
    } else if (val === 'tier_3') {
      next.set('min_rating', '2.8');
      next.set('max_rating', '3.7');
    } else if (val === 'tier_1_2') {
      next.set('max_rating', '2.7');
    }
    next.set('page', '1');
    setSearchParams(next);
  };

  // Curated genuine electronics brands per category
  const CATEGORY_BRANDS = {
    'Smartphones & Mobiles': ['Apple', 'Samsung', 'Motorola', 'Google', 'OnePlus', 'BLU', 'Xiaomi', 'LG'],
    'Laptops & Notebooks': ['HP', 'Lenovo', 'Dell', 'ASUS', 'Acer', 'Apple', 'MSI', 'Samsung', 'Toshiba', 'Microsoft', 'Gateway'],
    'Headphones & Earbuds': ['Sony', 'Bose', 'Apple', 'Beats', 'JBL', 'Panasonic', 'Soundcore', 'Skullcandy', 'Sennheiser'],
    'Cameras & Photography': ['Canon', 'Nikon', 'Sony', 'Fujifilm', 'Panasonic', 'GoPro', 'Blink'],
    'Hard Disks & Storage': ['SanDisk', 'Western Digital', 'Crucial', 'Seagate', 'Kingston', 'Samsung', 'PNY'],
    'Home Audio & Speakers': ['Bose', 'JBL', 'Sony', 'Ultimate Ears', 'Anker', 'DOSS'],
    'Smart Home & Devices': ['Amazon', 'Blink', 'Ring'],
    'Cables & Power Accessories': ['Anker', 'Amazon Basics', 'Belkin', 'Cable Matters'],
  };

  const ALL_CURATED_BRANDS = [
    'Apple', 'Samsung', 'HP', 'Lenovo', 'Dell', 'ASUS', 'Acer', 'Sony',
    'Bose', 'SanDisk', 'Western Digital', 'Canon', 'Nikon', 'JBL',
    'Motorola', 'Google', 'OnePlus', 'MSI', 'Crucial', 'Seagate',
    'Beats', 'Kingston', 'Microsoft', 'LG', 'GoPro', 'Fujifilm',
    'Panasonic', 'Anker', 'BLU', 'Xiaomi', 'Toshiba', 'Gateway'
  ];

  const availableBrands = categoryParam && CATEGORY_BRANDS[categoryParam]
    ? CATEGORY_BRANDS[categoryParam]
    : ALL_CURATED_BRANDS;

  const handleCategoryChange = (newCat) => {
    const next = new URLSearchParams(searchParams);
    if (newCat) {
      next.set('category', newCat);
      const catBrands = CATEGORY_BRANDS[newCat] || ALL_CURATED_BRANDS;
      if (brandParam && !catBrands.includes(brandParam)) {
        next.delete('brand');
      }
    } else {
      next.delete('category');
    }
    next.set('page', '1');
    setSearchParams(next);
  };

  // Strictly limited category list — only genuine categories where items are actually available in dataset
  const popularCategories = [
    { label: 'All Products', value: '' },
    { label: '💻 Laptops & Notebooks', value: 'Laptops & Notebooks' },
    { label: '📱 Smartphones & Mobiles', value: 'Smartphones & Mobiles' },
    { label: '🎧 Headphones & Earbuds', value: 'Headphones & Earbuds' },
    { label: '📷 Cameras & Photography', value: 'Cameras & Photography' },
    { label: '💾 Hard Disks & Storage', value: 'Hard Disks & Storage' },
    { label: '🔊 Home Audio & Speakers', value: 'Home Audio & Speakers' },
    { label: '📺 Smart Home & Devices', value: 'Smart Home & Devices' },
    { label: '🔌 Cables & Power Accessories', value: 'Cables & Power Accessories' },
  ];

  return (
    <div style={{ padding: '40px 0 80px 0' }}>
      <div className="container">
        {/* Header */}
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ fontSize: '2.4rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
            Electronics, Laptops & Mobiles
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.98rem' }}>
            Discover and inspect 8,866 electronics, laptops & smartphones cataloged with 9,733 in-depth customer reviews.
          </p>
        </div>

        {/* Main Search & Multi-Filter Box */}
        <div style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-md)',
          padding: '20px 24px',
          marginBottom: '20px',
          boxShadow: 'var(--shadow-sm)',
        }}>
          {/* Row 1: Search Bar in Box */}
          <form
            onSubmit={handleSearchSubmit}
            style={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'var(--bg-primary)',
              border: '1px solid var(--border-medium)',
              borderRadius: 'var(--radius-full)',
              padding: '6px 8px 6px 18px',
              marginBottom: '16px',
            }}
          >
            <Search
              size={18}
              color="var(--text-muted)"
              style={{ marginRight: '10px', flexShrink: 0 }}
            />
            <input
              type="text"
              placeholder="Search by title, brand, or model..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              style={{
                width: '100%',
                border: 'none',
                background: 'transparent',
                fontSize: '0.92rem',
                color: 'var(--text-primary)',
                outline: 'none',
              }}
            />
            {searchInput && (
              <button
                type="button"
                onClick={() => {
                  setSearchInput('');
                  updateParam('q', '');
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: '4px 8px',
                  fontSize: '0.85rem',
                }}
                title="Clear search"
              >
                ×
              </button>
            )}
            <button
              type="submit"
              className="btn btn-primary"
              style={{ padding: '8px 20px', fontSize: '0.85rem', borderRadius: 'var(--radius-full)' }}
            >
              Search
            </button>
          </form>

          {/* Row 2: Filter Dropdowns Below Search Bar */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            flexWrap: 'wrap',
          }}>
            {/* Category Select - Strictly 8 Available Categories in Catalog */}
            <div style={{ flex: '1 1 200px', minWidth: '180px' }}>
              <select
                value={categoryParam}
                onChange={(e) => handleCategoryChange(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 14px',
                  borderRadius: 'var(--radius-full)',
                  border: '1px solid var(--border-medium)',
                  backgroundColor: 'var(--bg-primary)',
                  fontSize: '0.86rem',
                  color: 'var(--text-primary)',
                  cursor: 'pointer',
                  outline: 'none',
                }}
              >
                <option value="">All Categories (8 Available)</option>
                <option value="Laptops & Notebooks">💻 Laptops & Notebooks</option>
                <option value="Smartphones & Mobiles">📱 Smartphones & Mobiles</option>
                <option value="Headphones & Earbuds">🎧 Headphones & Earbuds</option>
                <option value="Cameras & Photography">📷 Cameras & Photography</option>
                <option value="Hard Disks & Storage">💾 Hard Disks & Storage</option>
                <option value="Home Audio & Speakers">🔊 Home Audio & Speakers</option>
                <option value="Smart Home & Devices">📺 Smart Home & Devices</option>
                <option value="Cables & Power Accessories">🔌 Cables & Power Accessories</option>
              </select>
            </div>

            {/* Brand Select - Filtered strictly to genuine brands for the active category */}
            <div style={{ flex: '1 1 200px', minWidth: '180px' }}>
              <select
                value={brandParam}
                onChange={(e) => updateParam('brand', e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 14px',
                  borderRadius: 'var(--radius-full)',
                  border: '1px solid var(--border-medium)',
                  backgroundColor: 'var(--bg-primary)',
                  fontSize: '0.86rem',
                  color: 'var(--text-primary)',
                  cursor: 'pointer',
                  outline: 'none',
                }}
              >
                <option value="">All Brands ({availableBrands.length})</option>
                {availableBrands.map((b) => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>

            {/* Star Rating Select with fair 1★-5★ tiers */}
            <div style={{ flex: '1 1 180px', minWidth: '160px' }}>
              <select
                value={getRatingSelectValue()}
                onChange={(e) => handleRatingSelectChange(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 14px',
                  borderRadius: 'var(--radius-full)',
                  border: '1px solid var(--border-medium)',
                  backgroundColor: 'var(--bg-primary)',
                  fontSize: '0.86rem',
                  color: 'var(--text-primary)',
                  cursor: 'pointer',
                  outline: 'none',
                }}
              >
                <option value="">Any Star Rating</option>
                <option value="tier_5">🌟 5 Stars (4.5★ & Above)</option>
                <option value="tier_4">⚡ 4 Stars (3.8★ - 4.4★)</option>
                <option value="tier_3">⚖️ 3 Stars (2.8★ - 3.7★)</option>
                <option value="tier_1_2">⚠️ 1 & 2 Stars (Below 2.8★ — Low Rated)</option>
              </select>
            </div>

            {/* Reset Button */}
            {(queryParam || categoryParam || brandParam || minRatingParam || maxRatingParam) && (
              <div>
                <button
                  onClick={handleResetFilters}
                  className="btn btn-outline"
                  style={{ padding: '8px 14px', fontSize: '0.82rem', whiteSpace: 'nowrap' }}
                  title="Reset all filters"
                >
                  <RotateCcw size={14} style={{ marginRight: '6px' }} />
                  Reset
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Quick Category Navigation Pills */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          overflowX: 'auto',
          paddingBottom: '12px',
          marginBottom: '24px',
        }}>
          {popularCategories.map((c) => {
            const isSelected = categoryParam === c.value;
            return (
              <button
                key={c.label}
                onClick={() => handleCategoryChange(c.value)}
                style={{
                  padding: '8px 16px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.85rem',
                  fontWeight: isSelected ? 600 : 500,
                  backgroundColor: isSelected ? 'var(--text-primary)' : 'var(--bg-card)',
                  color: isSelected ? 'var(--bg-primary)' : 'var(--text-secondary)',
                  border: isSelected ? '1px solid var(--text-primary)' : '1px solid var(--border-light)',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease',
                  boxShadow: isSelected ? 'var(--shadow-sm)' : 'none',
                }}
              >
                {c.label}
              </button>
            );
          })}
        </div>

        {/* Active Search Query Badge (if searching from Homepage) */}
        {queryParam && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '20px',
            padding: '10px 18px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-light)',
            width: 'fit-content',
          }}>
            <span style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              Search query: <strong style={{ color: 'var(--text-primary)' }}>"{queryParam}"</strong> ({total} items found)
            </span>
            <button
              onClick={() => updateParam('q', '')}
              className="btn btn-outline"
              style={{ padding: '2px 8px', fontSize: '0.75rem', borderRadius: 'var(--radius-full)' }}
              title="Clear search query"
            >
              Clear ×
            </button>
          </div>
        )}

        {/* Laptops & Notebooks Section Editorial Callout */}
        {(categoryParam === 'Laptops & Notebooks' || categoryParam === 'Laptops' || categoryParam === 'Notebooks') && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 20px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-sage-subtle)',
            border: '1px solid rgba(135, 151, 122, 0.3)',
            marginBottom: '24px',
            fontSize: '0.88rem',
            color: 'var(--text-primary)',
          }}>
            <Laptop size={20} color="var(--accent-sage-dark)" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Laptops & Notebooks Section ({total} Products):</strong> Showing strictly verified laptops, notebooks, Chromebooks, 2-in-1s, and MacBooks (HP, Lenovo, Dell, ASUS, Acer, Apple, MSI, Alienware, Gateway). Laptop sleeves, backpacks, charger cables, stands, docks, cooling pads, and memory chips are strictly filtered out.
            </div>
            <button
              onClick={() => updateParam('category', '')}
              className="btn btn-outline"
              style={{ padding: '4px 12px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            >
              Clear Filter ×
            </button>
          </div>
        )}

        {/* Headphones & Earbuds Section Editorial Callout */}
        {categoryParam === 'Headphones & Earbuds' && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 20px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-sage-subtle)',
            border: '1px solid rgba(135, 151, 122, 0.3)',
            marginBottom: '24px',
            fontSize: '0.88rem',
            color: 'var(--text-primary)',
          }}>
            <Headphones size={20} color="var(--accent-sage-dark)" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Headphones & Earbuds Section ({total} Products):</strong> Showing strictly verified audio listening gear — wireless earbuds, over-ear, on-ear, and noise-canceling headphones. All non-listening accessories (cables, cases, adapters, and bags) are strictly filtered out.
            </div>
            <button
              onClick={() => updateParam('category', '')}
              className="btn btn-outline"
              style={{ padding: '4px 12px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            >
              Clear Filter ×
            </button>
          </div>
        )}

        {/* Smartphones & Mobiles Section Editorial Callout */}
        {(categoryParam === 'Smartphones & Mobiles' || categoryParam === 'Smartphones') && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 20px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-sage-subtle)',
            border: '1px solid rgba(135, 151, 122, 0.3)',
            marginBottom: '24px',
            fontSize: '0.88rem',
            color: 'var(--text-primary)',
          }}>
            <Smartphone size={20} color="var(--accent-sage-dark)" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Smartphones & Mobiles Section ({total} Products):</strong> Showing strictly verified unlocked smartphones, flagship 5G devices, and cellular phones (Apple iPhone, Samsung Galaxy, Google Pixel, Motorola, OnePlus, BLU, Xiaomi). Phone cases, screen protectors, cables, and chargers are strictly excluded.
            </div>
            <button
              onClick={() => updateParam('category', '')}
              className="btn btn-outline"
              style={{ padding: '4px 12px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            >
              Clear Filter ×
            </button>
          </div>
        )}

        {/* Cameras & Photography Section Editorial Callout */}
        {(categoryParam === 'Cameras & Photography' || categoryParam === 'Camera & Photo' || categoryParam === 'Cameras') && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 20px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-sage-subtle)',
            border: '1px solid rgba(135, 151, 122, 0.3)',
            marginBottom: '24px',
            fontSize: '0.88rem',
            color: 'var(--text-primary)',
          }}>
            <Camera size={20} color="var(--accent-sage-dark)" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Cameras & Photography Section ({total} Products):</strong> Showing strictly verified digital cameras, DSLRs, lenses, camcorders, action cameras, and webcams (Fujifilm, Canon, Nikon, Sony, Panasonic). Camera bags, straps, cases, and cleaning kits are strictly filtered out.
            </div>
            <button
              onClick={() => updateParam('category', '')}
              className="btn btn-outline"
              style={{ padding: '4px 12px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            >
              Clear Filter ×
            </button>
          </div>
        )}

        {/* Hard Disks & Storage Section Editorial Callout */}
        {(categoryParam === 'Hard Disks & Storage' || categoryParam === 'Hard Disk' || categoryParam === 'Storage') && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 20px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-sage-subtle)',
            border: '1px solid rgba(135, 151, 122, 0.3)',
            marginBottom: '24px',
            fontSize: '0.88rem',
            color: 'var(--text-primary)',
          }}>
            <HardDrive size={20} color="var(--accent-sage-dark)" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Hard Disks & Storage Section ({total} Products):</strong> Showing strictly verified internal/external hard drives, NVMe/SATA SSDs, high-speed flash drives, and MicroSD cards (SanDisk, Western Digital, Crucial, Seagate, Kingston). Laptop cases, enclosures, and mini PCs are strictly excluded.
            </div>
            <button
              onClick={() => updateParam('category', '')}
              className="btn btn-outline"
              style={{ padding: '4px 12px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            >
              Clear Filter ×
            </button>
          </div>
        )}

        {/* Home Audio & Speakers Section Editorial Callout */}
        {(categoryParam === 'Home Audio & Speakers' || categoryParam === 'Home Audio & Theater') && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 20px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-sage-subtle)',
            border: '1px solid rgba(135, 151, 122, 0.3)',
            marginBottom: '24px',
            fontSize: '0.88rem',
            color: 'var(--text-primary)',
          }}>
            <Volume2 size={20} color="var(--accent-sage-dark)" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Home Audio & Speakers Section ({total} Products):</strong> Showing strictly verified Bluetooth speakers, soundbars, subwoofers, and home audio systems (Bose, JBL, Sony, Ultimate Ears, DOSS). Headphones and audio cables are strictly filtered out.
            </div>
            <button
              onClick={() => updateParam('category', '')}
              className="btn btn-outline"
              style={{ padding: '4px 12px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            >
              Clear Filter ×
            </button>
          </div>
        )}

        {/* Smart Home & Devices Section Editorial Callout */}
        {(categoryParam === 'Smart Home & Devices' || categoryParam === 'Amazon Devices') && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 20px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-sage-subtle)',
            border: '1px solid rgba(135, 151, 122, 0.3)',
            marginBottom: '24px',
            fontSize: '0.88rem',
            color: 'var(--text-primary)',
          }}>
            <Tv size={20} color="var(--accent-sage-dark)" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Smart Home & Devices Section ({total} Products):</strong> Showing genuine smart displays, streaming media sticks, Kindles, and smart tablets (Amazon Echo, Fire TV, Kindle Paperwhite, Fire HD). Protective cases and remote covers are excluded.
            </div>
            <button
              onClick={() => updateParam('category', '')}
              className="btn btn-outline"
              style={{ padding: '4px 12px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            >
              Clear Filter ×
            </button>
          </div>
        )}

        {/* Cables & Power Accessories Section Editorial Callout */}
        {(categoryParam === 'Cables & Power Accessories' || categoryParam === 'Cables') && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 20px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-sage-subtle)',
            border: '1px solid rgba(135, 151, 122, 0.3)',
            marginBottom: '24px',
            fontSize: '0.88rem',
            color: 'var(--text-primary)',
          }}>
            <Plug size={20} color="var(--accent-sage-dark)" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Cables & Power Accessories Section ({total} Products):</strong> Showing verified high-speed HDMI cables, USB-C cords, fast power adapters, surge protectors, and multiport hubs (Amazon Basics, Anker, Belkin, Cable Matters).
            </div>
            <button
              onClick={() => updateParam('category', '')}
              className="btn btn-outline"
              style={{ padding: '4px 12px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            >
              Clear Filter ×
            </button>
          </div>
        )}

        {/* Generic Category Scope Indicator when any other category is chosen */}
        {categoryParam && categoryParam !== 'Headphones & Earbuds' && categoryParam !== 'Cell Phones & Accessories' && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '12px 18px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-card-subtle)',
            border: '1px solid var(--border-light)',
            marginBottom: '24px',
            fontSize: '0.86rem',
            color: 'var(--text-primary)',
          }}>
            <Layers size={18} color="var(--accent-sage)" style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              Scoped to category: <strong>{categoryParam}</strong> ({total} matching products) {queryParam && `• Searching for "${queryParam}"`}
            </div>
            <button
              onClick={() => updateParam('category', '')}
              className="btn btn-outline"
              style={{ padding: '4px 12px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            >
              Clear Category ×
            </button>
          </div>
        )}

        {/* Results Counter */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          fontSize: '0.88rem',
          color: 'var(--text-muted)',
        }}>
          <div>
            Showing <strong>{products.length}</strong> of <strong>{total.toLocaleString()}</strong> products
            {pageParam > 1 && ` (Page ${pageParam} of ${totalPages})`}
          </div>
        </div>

        {/* Product Grid */}
        {loading ? (
          <div className="grid-responsive-products">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <div key={i} className="skeleton" style={{ height: '360px' }} />
            ))}
          </div>
        ) : error ? (
          <div className="card" style={{ textAlign: 'center', padding: '48px', color: 'var(--accent-terracotta)' }}>
            <p style={{ fontSize: '1.1rem', marginBottom: '8px' }}>Failed to load products</p>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{error}</p>
          </div>
        ) : products.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '64px' }}>
            <h3 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>No products match your criteria</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
              Try broadening your keyword search or resetting category filters.
            </p>
            <button onClick={handleResetFilters} className="btn btn-outline">
              Clear All Filters
            </button>
          </div>
        ) : (
          <div className="grid-responsive-products">
            {products.map((product) => (
              <ProductCard key={product.product_id} product={product} />
            ))}
          </div>
        )}

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px',
            marginTop: '48px',
          }}>
            <button
              onClick={() => updateParam('page', String(pageParam - 1))}
              disabled={pageParam <= 1}
              className="btn btn-outline"
              style={{
                opacity: pageParam <= 1 ? 0.4 : 1,
                cursor: pageParam <= 1 ? 'not-allowed' : 'pointer',
                padding: '8px 16px',
              }}
            >
              <ChevronLeft size={16} />
              Previous
            </button>

            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Page <strong>{pageParam}</strong> of <strong>{totalPages}</strong>
            </span>

            <button
              onClick={() => updateParam('page', String(pageParam + 1))}
              disabled={pageParam >= totalPages}
              className="btn btn-outline"
              style={{
                opacity: pageParam >= totalPages ? 0.4 : 1,
                cursor: pageParam >= totalPages ? 'not-allowed' : 'pointer',
                padding: '8px 16px',
              }}
            >
              Next
              <ChevronRight size={16} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
