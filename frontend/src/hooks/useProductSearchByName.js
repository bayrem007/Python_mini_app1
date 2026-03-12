import { useState, useEffect } from 'react'
import { apiClient } from '../services/apiClient'

export function useProductSearchByName(searchTerms) {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!searchTerms) {
      setProducts([])
      setError(null)
      return
    }

    setLoading(true)
    setError(null)

    apiClient.searchProductsByName(searchTerms)
      .then((data) => {
        setProducts(data.products || [])
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setProducts([])
        setLoading(false)
      })
  }, [searchTerms])

  return { products, loading, error }
}
