import React from 'react';
import { Star, StarHalf } from 'lucide-react';

export default function StarRating({ rating = 0, max = 5, size = 16, showNumber = false }) {
  const numericRating = typeof rating === 'number' ? rating : parseFloat(rating) || 0;
  const stars = [];

  for (let i = 1; i <= max; i++) {
    if (numericRating >= i) {
      stars.push(
        <Star
          key={i}
          size={size}
          fill="var(--accent-gold)"
          color="var(--accent-gold)"
        />
      );
    } else if (numericRating >= i - 0.5) {
      stars.push(
        <StarHalf
          key={i}
          size={size}
          fill="var(--accent-gold)"
          color="var(--accent-gold)"
        />
      );
    } else {
      stars.push(
        <Star
          key={i}
          size={size}
          color="#D9D2C3"
        />
      );
    }
  }

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
      <div style={{ display: 'inline-flex', gap: '2px' }}>{stars}</div>
      {showNumber && (
        <span style={{
          fontSize: '0.85rem',
          fontWeight: 600,
          color: 'var(--text-primary)',
          marginLeft: '4px',
        }}>
          {numericRating.toFixed(1)}
        </span>
      )}
    </div>
  );
}

