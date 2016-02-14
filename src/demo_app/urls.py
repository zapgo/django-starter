from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    # url(r'^spreadsheet/$', views.spreadsheet),
    # url(r'client/(?P<pk>[0-9]+)/$', login_required(views.ThingDetailView.as_view()), name='thing_detail'),
]
