from django.shortcuts import render

from rest_framework import viewsets

from .models import Dream
from .serializers import DreamSerializer


class DreamViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Dream.objects.all()
    serializer_class = DreamSerializer
