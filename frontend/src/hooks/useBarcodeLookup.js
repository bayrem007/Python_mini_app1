import { useState, useEffect } from 'react'
import { apiClient } from '../services/apiClient'

export function useBarcodeLookup(barcode) {
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!barcode) {
      setProduct(null)
      setError(null)
      return
    }

    setLoading(true)
    setError(null)

    apiClient.getProductByBarcode(barcode)
      .then((data) => {
        setProduct(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setProduct(null)
        setLoading(false)
      })
  }, [barcode])

  return { product, loading, error }
}
