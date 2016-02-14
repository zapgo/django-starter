from rest_framework import serializers

from demo_app.models import Dream
from .models import Job


class JobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job


class DreamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dream
