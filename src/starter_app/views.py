from collections import OrderedDict
from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def api_root(request, format=None):
    """
    ### API documentation for the Django Starter.
    ---
    """
    return Response()


def index(request):

    context_dict = {}

    return render(request, 'starter_app/index.html', context=context_dict)