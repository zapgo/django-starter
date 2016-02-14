from rest_framework import mixins, viewsets
from .models import Dream, Job
from .serializers import DreamSerializer, JobSerializer


class JobViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    API endpoint that allows jobs to be viewed or created.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class DreamViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Dream.objects.all()
    serializer_class = DreamSerializer
