from __future__ import annotations

from typing import Optional

from mongoengine.queryset.visitor import Q

from products.models import Product
from substitutions.models import Substitution
from users.models import User


_NUTRISCORE_ORDER = ["a", "b", "c", "d", "e"]


class SubstitutionService:
    """
    Find healthier substitutes based on NutriScore, allergens and category.
    """

    def __init__(self) -> None:
        pass

    def find_substitute(self, product_id: str) -> Optional[dict]:
        """
        Return the best substitute for the given product_id or None.

        Output dict contains:
        - substitute (full product dict)
        - description
        - brand
        - openfoodfacts_url
        """

        original = Product.objects(id=product_id).first()
        if not original or not original.category:
            return None

        original_score = (original.nutriscore or "e").lower()
        try:
            original_index = _NUTRISCORE_ORDER.index(original_score)
        except ValueError:
            original_index = _NUTRISCORE_ORDER.index("e")

        # Step 2+3: same category, better NutriScore, exclude self.
        better_candidates = Product.objects(
            Q(category=original.category)
            & Q(id__ne=original.id)
            & Q(nutriscore__in=_NUTRISCORE_ORDER[:original_index])
        )

        if not better_candidates:
            return None

        def score_key(p: Product):
            # Lower index = better NutriScore; fewer allergens = better.
            score = (p.nutriscore or "e").lower()
            try:
                idx = _NUTRISCORE_ORDER.index(score)
            except ValueError:
                idx = _NUTRISCORE_ORDER.index("e")

            allergens_count = len(p.allergens or [])
            return (idx, allergens_count, p.name.lower())

        best = sorted(better_candidates, key=score_key)[0]

        return {
            "substitute": {
                "id": str(best.id),
                "name": best.name,
                "brand": best.brand,
                "barcode": best.barcode,
                "nutriscore": best.nutriscore,
                "allergens": best.allergens or [],
                "ingredients": best.ingredients or [],
                "category": best.category,
                "image_url": best.image_url,
                "openfoodfacts_url": best.openfoodfacts_url,
            },
            "description": best.name,
            "brand": best.brand,
            "openfoodfacts_url": best.openfoodfacts_url,
        }


def save_substitution(user_id: str, original: Product, substitute: Product) -> Substitution:
    user = User.objects(id=user_id).first()
    if not user:
        raise ValueError("User not found")

    sub = Substitution(
        user=user,
        original_product=original,
        substitute_product=substitute,
    )
    sub.save()
    return sub

