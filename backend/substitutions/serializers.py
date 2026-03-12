from __future__ import annotations

from rest_framework import serializers

from products.serializers import ProductSerializer


class SubstitutionResultSerializer(serializers.Serializer):
    original = serializers.DictField()
    substitutes = serializers.ListField(child=serializers.DictField())

    @staticmethod
    def build(original, substitutes) -> dict:
        return {
            "original": ProductSerializer.from_document(original),
            "substitutes": [ProductSerializer.from_document(p) for p in substitutes],
        }

