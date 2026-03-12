from __future__ import annotations

from typing import Optional

from django.conf import settings
from mongoengine import connect


_CONNECTED_ALIAS: Optional[str] = None


def ensure_mongo_connected() -> str:
    """
    Connect MongoEngine once per Django process.

    This keeps MongoDB access in a dedicated data-access layer (MongoEngine),
    while Django's ORM can still power auth/admin/etc if desired.
    """

    global _CONNECTED_ALIAS
    if _CONNECTED_ALIAS is not None:
        return _CONNECTED_ALIAS

    uri = getattr(settings, "MONGODB_URI", "") or ""
    db_name = getattr(settings, "MONGODB_DB_NAME", "purbeurre")
    timeout_ms = int(getattr(settings, "MONGODB_CONNECT_TIMEOUT_MS", 20000))

    if not uri:
        # Fallback for local/dev: define a default connection so MongoEngine APIs work.
        # If you intend to use Atlas, set MONGODB_URI in your .env.
        uri = f"mongodb://localhost:27017/{db_name}"

    connect(
        db=db_name,
        host=uri,
        alias="default",
        uuidRepresentation="standard",
        connectTimeoutMS=timeout_ms,
        serverSelectionTimeoutMS=timeout_ms,
    )
    _CONNECTED_ALIAS = "default"
    return _CONNECTED_ALIAS

