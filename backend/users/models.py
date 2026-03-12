from __future__ import annotations

from datetime import datetime

from mongoengine import DateTimeField, Document, EmailField, StringField


class User(Document):
    """
    Application user stored in MongoDB.

    Note: Django's built-in auth/admin can remain enabled on a SQL DB, but this
    document is the domain user for the app itself.
    """

    meta = {
        "collection": "users",
        "indexes": [
            {"fields": ["username"], "unique": True},
            {"fields": ["email"], "unique": True, "sparse": True},
            "created_at",
        ],
    }

    username = StringField(required=True, min_length=3, max_length=150)
    email = EmailField(required=False)
    password = StringField(required=True)  # store a hash, not plaintext
    created_at = DateTimeField(default=datetime.utcnow)

    def __str__(self) -> str:  # pragma: no cover
        return self.username
