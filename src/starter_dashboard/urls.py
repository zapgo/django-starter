from django.conf.urls import patterns, url

from starter_dashboard import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^tables/$', views.tables, name='tables'),
    url(r'^forms/$', views.forms, name='forms'),
    url(r'^alerts/$', views.alerts, name='alerts'),
    url(r'^charts/$', views.charts, name='charts'),
)

