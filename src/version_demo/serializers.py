from rest_framework import serializers

from .models import Dream


class DreamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dream
