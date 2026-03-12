const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

async function request(path, { method = 'GET', body } = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const payload = await res.json()
      message = payload?.detail || payload?.message || message
    } catch {
      // ignore
    }
    throw new Error(message)
  }

  return res.json()
}

export const apiClient = {
  searchProducts: (q, limit = 20) =>
    request(`/products/search/?q=${encodeURIComponent(q)}&limit=${encodeURIComponent(limit)}`),
  getSubstitutions: (productId, limit = 10) =>
    request(`/substitutions/?product_id=${encodeURIComponent(productId)}&limit=${encodeURIComponent(limit)}`),
  getProductByBarcode: (barcode) =>
    request(`/products/barcode/${encodeURIComponent(barcode)}/test/`),
  searchProductsByName: (searchTerms) =>
    request(`/products/name/${encodeURIComponent(searchTerms)}/`),
}

