from __future__ import annotations

from datetime import datetime

from mongoengine import DateTimeField, Document, ListField, StringField, URLField


class Product(Document):
    """
    Product stored in MongoDB (Atlas).
    """

    meta = {
        "collection": "products",
        "indexes": [
            "name",
            "brand",
            {"fields": ["barcode"], "unique": True},
            "nutriscore",
            "category",
            {"fields": ["name", "brand"], "sparse": True},
        ],
    }

    name = StringField(required=True)
    brand = StringField(required=False)
    barcode = StringField(required=True)  # OpenFoodFacts "code" / barcode
    nutriscore = StringField(required=False, choices=list("abcde"))
    allergens = ListField(StringField(), default=list)
    ingredients = ListField(StringField(), default=list)
    category = StringField(required=False)
    image_url = URLField(required=False)
    openfoodfacts_url = URLField(required=False)
    created_at = DateTimeField(default=datetime.utcnow)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.barcode})"
