"""
WSGI config for purbeurre project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'purbeurre.settings')

from purbeurre.mongo import ensure_mongo_connected

ensure_mongo_connected()

application = get_wsgi_application()
