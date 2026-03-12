import { useState } from 'react'
import { useBarcodeLookup } from '../../hooks/useBarcodeLookup'
import { useProductSearchByName } from '../../hooks/useProductSearchByName'

export function BarcodeLookup({ onProductFound }) {
  const [searchType, setSearchType] = useState('barcode') // 'barcode' or 'name'
  const [searchValue, setSearchValue] = useState('')
  
  const { product: barcodeProduct, loading: barcodeLoading, error: barcodeError } = useBarcodeLookup(
    searchType === 'barcode' ? searchValue : null
  )
  const { products: nameProducts, loading: nameLoading, error: nameError } = useProductSearchByName(
    searchType === 'name' ? searchValue : null
  )

  const handleSubmit = (e) => {
    e.preventDefault()
    if (searchValue.trim()) {
      // Trigger search by setting the search value
      setSearchValue(searchValue.trim())
    }
  }

  const handleInputChange = (e) => {
    setSearchValue(e.target.value)
  }

  const handleSearch = () => {
    if (searchValue.trim()) {
      setSearchValue(searchValue.trim())
    }
  }

  const loading = searchType === 'barcode' ? barcodeLoading : nameLoading
  const error = searchType === 'barcode' ? barcodeError : nameError

  const getNutriScoreColor = (nutriscore) => {
    if (!nutriscore) return '#666'
    switch (nutriscore.toLowerCase()) {
      case 'a': return 'green'
      case 'b': return 'lightgreen'
      case 'c': return 'yellow'
      case 'd': return 'orange'
      case 'e': return 'red'
      default: return '#666'
    }
  }

  return (
    <div style={{ marginBottom: 24, padding: 16, border: '1px solid #ddd', borderRadius: 8 }}>
      <h3>Product Search</h3>
      
      <div style={{ marginBottom: 12 }}>
        <label style={{ marginRight: 16 }}>
          <input
            type="radio"
            value="barcode"
            checked={searchType === 'barcode'}
            onChange={(e) => setSearchType(e.target.value)}
            style={{ marginRight: 8 }}
          />
          Search by Barcode
        </label>
        <label>
          <input
            type="radio"
            value="name"
            checked={searchType === 'name'}
            onChange={(e) => setSearchType(e.target.value)}
            style={{ marginRight: 8 }}
          />
          Search by Name
        </label>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input
          type="text"
          value={searchValue}
          onChange={handleInputChange}
          placeholder={
            searchType === 'barcode' 
              ? "Enter barcode (e.g., 737628064502)" 
              : "Enter product name (e.g., peanut butter)"
          }
          style={{ flex: 1, padding: 8, fontSize: 16 }}
        />
        <button 
          onClick={handleSearch}
          disabled={loading || !searchValue.trim()}
          style={{ 
            padding: '8px 16px', 
            fontSize: 16, 
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: 4,
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {error && (
        <div style={{ color: 'crimson', marginBottom: 12 }}>
          Error: {error}
        </div>
      )}

      {/* Barcode search result */}
      {searchType === 'barcode' && barcodeProduct && (
        <div style={{ 
          padding: 12, 
          backgroundColor: '#f8f9fa', 
          borderRadius: 4,
          border: '1px solid #dee2e6'
        }}>
          <h4>Product Found:</h4>
          <p><strong>Name:</strong> {barcodeProduct.name}</p>
          <p><strong>Brand:</strong> {barcodeProduct.brand}</p>
          <p><strong>Barcode:</strong> {barcodeProduct.barcode}</p>
          <p><strong>Nutriscore:</strong> <span style={{ 
            fontWeight: 'bold', 
            color: getNutriScoreColor(barcodeProduct.nutriscore)
          }}>{barcodeProduct.nutriscore?.toUpperCase()}</span></p>
          <p><strong>Categories:</strong> {barcodeProduct.categories}</p>
          <p><strong>Countries:</strong> {barcodeProduct.countries}</p>
          <p><strong>Available in France:</strong> {barcodeProduct.is_french ? '✅ Yes' : '❌ No'}</p>
        </div>
      )}

      {/* Name search results */}
      {searchType === 'name' && nameProducts.length > 0 && (
        <div>
          <h4>Found {nameProducts.length} products:</h4>
          <div style={{ display: 'grid', gap: 12 }}>
            {nameProducts.map((product, index) => (
              <div key={index} style={{ 
                padding: 12, 
                backgroundColor: '#f8f9fa', 
                borderRadius: 4,
                border: '1px solid #dee2e6'
              }}>
                <p><strong>Name:</strong> {product.name}</p>
                <p><strong>Brand:</strong> {product.brand}</p>
                <p><strong>Barcode:</strong> {product.barcode}</p>
                <p><strong>Nutriscore:</strong> <span style={{ 
                  fontWeight: 'bold', 
                  color: getNutriScoreColor(product.nutriscore)
                }}>{product.nutriscore?.toUpperCase()}</span></p>
                <p><strong>Categories:</strong> {product.categories}</p>
                <p><strong>Available in France:</strong> {product.is_french ? '✅ Yes' : '❌ No'}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {searchType === 'name' && !nameLoading && nameProducts.length === 0 && searchValue && !error && (
        <div style={{ color: '#666', fontStyle: 'italic' }}>
          No products found for "{searchValue}"
        </div>
      )}
    </div>
  )
}
