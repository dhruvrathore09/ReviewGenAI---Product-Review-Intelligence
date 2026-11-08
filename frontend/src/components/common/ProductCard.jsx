import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, MessageSquare, Tag, Package } from 'lucide-react';
import StarRating from './StarRating';

export default function ProductCard({ product }) {
  const [imgError, setImgError] = useState(false);

  const priceFormatted = product.price != null
    ? `$${Number(product.price).toFixed(2)}`
    : 'Price Unavailable';

  return (
    <div className="card" style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      padding: '20px',
      height: '100%',
    }}>
      <div>
        {/* Product Image Container */}
        <div style={{
          width: '100%',
          height: '190px',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: '#F9F7F2',
          border: '1px solid var(--border-light)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
          marginBottom: '16px',
          position: 'relative',
        }}>
          {product.image_url && !imgError ? (
            <img
              src={product.image_url}
              alt={product.product_name}
              onError={() => setImgError(true)}
              style={{
                maxWidth: '90%',
                maxHeight: '90%',
                objectFit: 'contain',
                transition: 'transform 0.3s ease',
              }}
            />
          ) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '8px',
              color: 'var(--text-muted)',
            }}>
              <Package size={32} strokeWidth={1.5} />
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {product.brand || 'Electronics'}
              </span>
            </div>
          )}

          {product.db_review_count > 0 && (
            <span style={{
              position: 'absolute',
              top: '10px',
              right: '10px',
              backgroundColor: 'rgba(37, 40, 32, 0.85)',
              color: 'var(--bg-primary)',
              padding: '3px 8px',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.7rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}>
              <MessageSquare size={10} />
              {product.db_review_count} Analyzed
            </span>
          )}
        </div>

        {/* Category & Brand Metadata */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '8px',
          flexWrap: 'wrap',
        }}>
          {product.brand && (
            <span className="badge badge-sage" style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
              {product.brand}
            </span>
          )}
          {product.main_category && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {product.main_category}
            </span>
          )}
        </div>

        {/* Product Title */}
        <Link to={`/products/${product.product_id}`}>
          <h3 style={{
            fontSize: '1rem',
            fontWeight: 600,
            lineHeight: 1.4,
            marginBottom: '8px',
            color: 'var(--text-primary)',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            fontFamily: 'var(--font-sans)',
            cursor: 'pointer',
          }}>
            {product.product_name}
          </h3>
        </Link>
      </div>

      <div>
        {/* Rating and Price Footer */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '16px',
          paddingTop: '12px',
          borderTop: '1px solid var(--border-light)',
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{
                fontFamily: 'var(--font-serif)',
                fontSize: '1.05rem',
                fontWeight: 700,
                color: 'var(--text-primary)',
              }}>
                {product.honest_rating != null ? `${product.honest_rating.toFixed(1)}★` : `${(product.average_rating || 0).toFixed(1)}★`}
              </span>
              <span style={{
                fontSize: '0.68rem',
                color: '#B25E46',
                backgroundColor: '#FDF2F0',
                padding: '1px 6px',
                borderRadius: 'var(--radius-full)',
                fontWeight: 600,
                border: '1px solid rgba(200, 109, 86, 0.3)',
              }}>
                Honest Rating
              </span>
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Amazon Listed: {product.average_rating != null ? `${product.average_rating.toFixed(1)}★` : 'N/A'}
              {product.rating_number ? ` • ${product.rating_number.toLocaleString()}` : ''}
            </div>
          </div>

          <div style={{
            fontFamily: 'var(--font-serif)',
            fontSize: '1.15rem',
            fontWeight: 600,
            color: 'var(--text-primary)',
          }}>
            {priceFormatted}
          </div>
        </div>

        {/* Action Button */}
        <Link
          to={`/products/${product.product_id}`}
          className="btn btn-outline"
          style={{ width: '100%', fontSize: '0.85rem', padding: '8px 14px' }}
        >
          View Intelligence
          <ArrowUpRight size={14} />
        </Link>
      </div>
    </div>
  );
}

