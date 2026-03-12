from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional

import requests
from requests import Response

from products.models import Product


OPENFOODFACTS_BASE_URL = "https://world.openfoodfacts.org"


@dataclass(frozen=True)
class LoadResult:
    imported_products: int
    failed_products: int


class OpenFoodFactsService:
    """
    Service responsible for fetching and persisting OpenFoodFacts products.

    Responsibilities:
    - Fetch product data from the OpenFoodFacts API
    - Filter only French products
    - Extract and normalize useful fields
    - Insert/update them in MongoDB
    """

    def __init__(
        self,
        base_url: str = OPENFOODFACTS_BASE_URL,
        session: Optional[requests.Session] = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout

    # ---------- HTTP helpers ----------

    def _get(self, path: str, params: Optional[dict[str, Any]] = None) -> Optional[Response]:
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.get(url, params=params or {}, timeout=self.timeout)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException:
            # In production you would log this instead of silently returning None.
            return None

    # ---------- Public API ----------

    def fetch_products_by_category(
        self,
        category: str,
        page_size: int = 100,
        page: int = 1,
    ) -> List[dict[str, Any]]:
        """
        Fetch a *slice* of products for a given OFF category tag.

        We keep page_size modest and let callers iterate pages to avoid
        downloading the entire dataset.
        """

        params = {"page_size": page_size, "page": page, "json": 1}
        resp = self._get(f"/category/{category}.json", params=params)
        if resp is None:
            return []

        try:
            data = resp.json()
        except ValueError:
            return []

        products = data.get("products") or []

        # Filter to French products only.
        filtered: List[dict[str, Any]] = []
        for p in products:
            if self._is_french_product(p):
                filtered.append(p)
        return filtered

    def fetch_product_by_barcode(self, barcode: str) -> Optional[dict[str, Any]]:
        """
        Fetch a single product by its barcode from the OpenFoodFacts API.
        
        Returns the raw product data if found, None otherwise.
        """
        resp = self._get(f"/api/v0/product/{barcode}")
        if resp is None:
            return None

        try:
            data = resp.json()
        except ValueError:
            return None

        # Check if product was found
        if data.get("status") != 1:
            return None
            
        product = data.get("product")
        if not product:
            return None
            
        # Only return French products
        if self._is_french_product(product):
            return product
        return None

    def search_products_by_name(self, search_terms: str, page_size: int = 20, page: int = 1) -> List[dict[str, Any]]:
        """
        Search for products by name using OpenFoodFacts API.
        
        Returns list of French products matching the search terms.
        """
        params = {
            "search_terms": search_terms,
            "page_size": page_size,
            "page": page,
            "json": 1,
            "countries": "fr"  # Filter for French products
        }
        
        resp = self._get("/cgi/search.pl", params=params)
        if resp is None:
            return []

        try:
            data = resp.json()
        except ValueError:
            return []

        products = data.get("products") or []
        
        # Additional filtering to ensure only French products
        filtered: List[dict[str, Any]] = []
        for p in products:
            if self._is_french_product(p):
                filtered.append(p)
        
        return filtered

    def clean_product_data(self, product: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Normalize a raw OFF product into the minimal schema we store.

        We keep only:
        - name
        - brand
        - barcode
        - nutriscore
        - allergens
        - ingredients
        - category
        - image_url
        - openfoodfacts_url
        """

        code = str(product.get("code") or "").strip()
        name = (product.get("product_name") or product.get("generic_name") or "").strip()
        if not code or not name:
            return None

        allergens_raw = product.get("allergens") or ""
        allergens = [a.strip() for a in str(allergens_raw).split(",") if a.strip()]

        ingredients_raw = product.get("ingredients_text") or ""
        ingredients = [s.strip() for s in str(ingredients_raw).split(",") if s.strip()]

        categories_raw = product.get("categories") or ""
        category = (str(categories_raw).split(",")[0].strip() if categories_raw else "") or None

        return {
            "name": name,
            "brand": (product.get("brands") or "").strip(),
            "barcode": code,
            "nutriscore": (product.get("nutriscore_grade") or "").lower() or None,
            "allergens": allergens,
            "ingredients": ingredients,
            "category": category,
            "image_url": product.get("image_url") or None,
            "openfoodfacts_url": product.get("url") or None,
        }

    def save_products(self, products: Iterable[dict[str, Any]]) -> LoadResult:
        """
        Upsert a collection of already-cleaned product dicts into MongoDB.
        """

        imported = 0
        failed = 0

        for p in products:
            try:
                barcode = str(p.get("barcode") or "").strip()
                if not barcode:
                    failed += 1
                    continue

                doc = Product.objects(barcode=barcode).first() or Product(barcode=barcode)
                doc.name = p.get("name") or doc.name
                doc.brand = p.get("brand") or ""
                doc.nutriscore = p.get("nutriscore")
                doc.allergens = p.get("allergens") or []
                doc.ingredients = p.get("ingredients") or []
                doc.category = p.get("category")
                doc.image_url = p.get("image_url")
                doc.openfoodfacts_url = p.get("openfoodfacts_url")
                doc.save()
                imported += 1
            except Exception:
                # In production, log exception details here.
                failed += 1

        return LoadResult(imported_products=imported, failed_products=failed)

    def fetch_and_save_product_by_barcode(self, barcode: str) -> Optional[Product]:
        """
        Fetch a product by barcode from OpenFoodFacts and save it to MongoDB.
        
        Returns the saved Product document if successful, None otherwise.
        """
        # Fetch raw product data
        raw_product = self.fetch_product_by_barcode(barcode)
        if not raw_product:
            return None
            
        # Clean the product data
        cleaned_product = self.clean_product_data(raw_product)
        if not cleaned_product:
            return None
            
        # Save to database
        result = self.save_products([cleaned_product])
        if result.imported_products > 0:
            return Product.objects(barcode=barcode).first()
        
        return None

    # ---------- Internal helpers ----------

    @staticmethod
    def _is_french_product(product: dict[str, Any]) -> bool:
        """
        Determine whether a product should be considered French.

        We prefer `countries_tags` when available, but also fall back to
        searching the free-text `countries` field.
        """

        countries_tags = product.get("countries_tags") or []
        if any(tag.lower() == "en:france" or tag.lower().endswith(":france") for tag in countries_tags):
            return True

        countries = (product.get("countries") or "").lower()
        return "france" in countries
