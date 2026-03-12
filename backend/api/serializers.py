from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class SubstitutionFindRequestSerializer(serializers.Serializer):
    product_id = serializers.CharField()


class SubstitutionSaveRequestSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    substitute_id = serializers.CharField()

