from rest_framework import serializers


class LoadResultSerializer(serializers.Serializer):
    imported_products = serializers.IntegerField()
    imported_categories = serializers.IntegerField()

