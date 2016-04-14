from django.shortcuts import render


def index(request):

    context_dict = {}

    return render(request, 'starter_app/index.html', context=context_dict)