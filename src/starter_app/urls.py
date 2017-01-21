from django.conf.urls import patterns, url

from starter_app import views

urlpatterns = patterns(
    '',
    url(r'^$', views.api_root),
    url(r'^$', views.index, name='index'),
)