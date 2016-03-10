from django.http import JsonResponse
from rest_framework import mixins, viewsets
from .models import Dream, Job
from .serializers import DreamSerializer, JobSerializer
from .models import Thing


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


class ThingDetailView(DetailView):
    model = Thing


class ThingUpdateView(UpdateView):
    model = Thing
    fields = '__all__'


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        return context['object'].data


class ThingUpdateJsonView(JSONResponseMixin, UpdateView):
    model = Thing
    fields = ['data', ]

    def render_to_response(self, context, **response_kwargs):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format') == 'json':
            return self.render_to_json_response(context)
        else:
            return super().render_to_response(context)

        # return self.render_to_json_response(context, **response_kwargs)
