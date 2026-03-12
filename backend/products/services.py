from __future__ import annotations

from typing import Iterable, Optional

from mongoengine.queryset.visitor import Q

from products.models import Product


def get_product_by_id(product_id: str) -> Optional[Product]:
    try:
        return Product.objects(id=product_id).first()
    except Exception:
        return None


def get_product_by_barcode(barcode: str) -> Optional[Product]:
    return Product.objects(barcode=barcode).first()


def search_products(query: str, limit: int = 20) -> Iterable[Product]:
    q = (query or "").strip()
    if not q:
        return Product.objects.order_by("-created_at")[:limit]

    # Basic text-ish search without requiring MongoDB text indexes.
    return Product.objects(
        Q(name__icontains=q) | Q(brand__icontains=q) | Q(barcode__icontains=q)
    ).limit(limit)


def list_healthier_substitutes(
    product: Product, limit: int = 10
) -> Iterable[Product]:
    """
    Heuristic: look in same category and return products with better nutriscore.
    """

    if not product.category:
        return []

    grade = (product.nutriscore or "e").lower()
    better_grades = [g for g in "abcde" if g < grade]

    return (
        Product.objects(category=product.category, nutriscore__in=better_grades)
        .order_by("nutriscore", "-created_at")
        .limit(limit)
    )

