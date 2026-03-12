import { useMemo, useState } from 'react'
import { SearchBar } from '../../components/SearchBar/SearchBar'
import { ProductCard } from '../../components/ProductCard/ProductCard'
import { BarcodeLookup } from '../../components/BarcodeLookup/BarcodeLookup'
import { useProductsSearch } from '../../hooks/useProductsSearch'
import { useSubstitutions } from '../../hooks/useSubstitutions'

export function HomePage() {
  const [query, setQuery] = useState('')
  const { products, loading: searching, error: searchError } = useProductsSearch(query)

  const [selectedProductId, setSelectedProductId] = useState(null)
  const { result, loading: loadingSubs, error: subsError } = useSubstitutions(selectedProductId)

  const selected = useMemo(
    () => products.find((p) => p.id === selectedProductId) ?? null,
    [products, selectedProductId],
  )

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: 24 }}>
      <h1>Pur Beurre - Healthy Food Substitution</h1>
      <p>Search for a product, then view healthier substitutes.</p>

      <BarcodeLookup />

      <hr style={{ margin: '24px 0' }} />

      <h2>Search Products</h2>
      <SearchBar value={query} onChange={setQuery} placeholder="Search products (name or brand)..." />

      {searchError ? <p style={{ color: 'crimson' }}>{searchError}</p> : null}
      {searching ? <p>Searching...</p> : null}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
        {products.map((p) => (
          <ProductCard
            key={p.id}
            product={p}
            selected={p.id === selectedProductId}
            onSelect={() => setSelectedProductId(p.id)}
          />
        ))}
      </div>

      {selected ? (
        <div style={{ marginTop: 32 }}>
          <h2>Substitutes for: {selected.name}</h2>
          {subsError ? <p style={{ color: 'crimson' }}>{subsError}</p> : null}
          {loadingSubs ? <p>Loading substitutes...</p> : null}

          {result?.substitutes?.length ? (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: 16,
              }}
            >
              {result.substitutes.map((p) => (
                <ProductCard key={p.id} product={p} selected={false} onSelect={() => {}} />
              ))}
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}

