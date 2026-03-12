export function ProductCard({ product, selected, onSelect }) {
  return (
    <button
      onClick={onSelect}
      type="button"
      style={{
        textAlign: 'left',
        padding: 16,
        borderRadius: 12,
        border: selected ? '2px solid #4f46e5' : '1px solid #e5e7eb',
        background: 'white',
        cursor: 'pointer',
      }}
    >
      <div style={{ display: 'flex', gap: 12 }}>
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            style={{ width: 64, height: 64, objectFit: 'cover', borderRadius: 10, background: '#f3f4f6' }}
          />
        ) : (
          <div style={{ width: 64, height: 64, borderRadius: 10, background: '#f3f4f6' }} />
        )}

        <div style={{ minWidth: 0 }}>
          <div style={{ fontWeight: 650, marginBottom: 4, lineHeight: 1.2 }}>{product.name}</div>
          <div style={{ color: '#6b7280', fontSize: 14, marginBottom: 8 }}>
            {product.brands ? product.brands : '—'}
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {product.nutriscore_grade ? (
              <span style={{ fontSize: 12, padding: '3px 8px', borderRadius: 999, background: '#eef2ff' }}>
                Nutri-Score: {product.nutriscore_grade.toUpperCase()}
              </span>
            ) : null}
            {product.nova_group ? (
              <span style={{ fontSize: 12, padding: '3px 8px', borderRadius: 999, background: '#ecfeff' }}>
                NOVA: {product.nova_group}
              </span>
            ) : null}
          </div>
        </div>
      </div>
    </button>
  )
}

