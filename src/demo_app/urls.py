from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'data/log/(?P<pk>[0-9]+)/view/$', login_required(views.ThingDetailView.as_view()), name='thing_detail'),
    url(r'data/log/(?P<pk>[0-9]+)/update/$', login_required(views.ThingUpdateView.as_view()), name='thing_update'),
    url(r'data/log/(?P<pk>[0-9]+)/json/$', login_required(views.ThingUpdateJsonView.as_view()), name='data_update'),

]
