from __future__ import annotations

from rest_framework import serializers

from products.models import Product


class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    brand = serializers.CharField(allow_blank=True, required=False)
    barcode = serializers.CharField()
    nutriscore = serializers.CharField(required=False, allow_blank=True)
    allergens = serializers.ListField(child=serializers.CharField(), required=False)
    ingredients = serializers.ListField(child=serializers.CharField(), required=False)
    category = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_null=True)
    openfoodfacts_url = serializers.URLField(required=False, allow_null=True)

    @staticmethod
    def from_document(product: Product) -> dict:
        return {
            "id": str(product.id),
            "name": product.name,
            "brand": product.brand or "",
            "barcode": product.barcode,
            "nutriscore": product.nutriscore,
            "allergens": product.allergens or [],
            "ingredients": product.ingredients or [],
            "category": product.category or "",
            "image_url": product.image_url,
            "openfoodfacts_url": product.openfoodfacts_url,
        }

