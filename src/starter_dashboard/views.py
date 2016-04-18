from django.shortcuts import render, render_to_response
from django.template import RequestContext


def index(request):

    context_dict = {}

    return render(request, 'starter_dashboard/index.html', context=context_dict)


def tables(request):

    nav_id = 'nav_tables'
    page_id = 'page_tables'

    context = RequestContext(request)
    context_dict = {'nav_id': nav_id, 'page_id': page_id}

    return render_to_response('starter_dashboard/tables.html', context_dict, context)


def forms(request):

    nav_id = 'nav_forms'
    page_id = 'page_forms'

    context = RequestContext(request)
    context_dict = {'nav_id': nav_id, 'page_id': page_id}

    return render_to_response('starter_dashboard/forms.html', context_dict, context)


def alerts(request):

    nav_id = 'nav_alerts'
    page_id = 'page_alerts'

    context = RequestContext(request)
    context_dict = {'nav_id': nav_id, 'page_id': page_id}

    return render_to_response('starter_dashboard/alerts.html', context_dict, context)


def charts(request):

    nav_id = 'nav_charts'
    page_id = 'page_charts'

    context = RequestContext(request)
    context_dict = {'nav_id': nav_id, 'page_id': page_id}

    return render_to_response('starter_dashboard/charts.html', context_dict, context)

