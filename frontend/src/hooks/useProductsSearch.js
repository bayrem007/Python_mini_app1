import { useEffect, useState } from 'react'
import { apiClient } from '../services/apiClient'

export function useProductsSearch(query) {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const q = (query || '').trim()
    if (!q) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setProducts([])
      setLoading(false)
      setError(null)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    const t = setTimeout(() => {
      apiClient
        .searchProducts(q, 20)
        .then((data) => {
          if (!cancelled) setProducts(Array.isArray(data) ? data : [])
        })
        .catch((e) => {
          if (!cancelled) setError(e.message || 'Search failed')
        })
        .finally(() => {
          if (!cancelled) setLoading(false)
        })
    }, 250)

    return () => {
      cancelled = true
      clearTimeout(t)
    }
  }, [query])

  return { products, loading, error }
}

