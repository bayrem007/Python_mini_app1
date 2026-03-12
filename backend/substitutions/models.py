from __future__ import annotations

from datetime import datetime

from mongoengine import DateTimeField, Document, ReferenceField

from products.models import Product
from users.models import User


class Substitution(Document):
    """
    A user-specific substitution record.
    """

    meta = {
        "collection": "substitutions",
        "indexes": [
            {"fields": ["user", "original_product", "substitute_product"], "unique": True},
            "user",
            "original_product",
            "substitute_product",
            "created_at",
        ],
    }

    user = ReferenceField(User, required=True, reverse_delete_rule=2)
    original_product = ReferenceField(Product, required=True, reverse_delete_rule=2)
    substitute_product = ReferenceField(Product, required=True, reverse_delete_rule=2)
    created_at = DateTimeField(default=datetime.utcnow)
