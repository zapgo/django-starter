from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from reversion.admin import VersionAdmin
from .models import Dream


# from .models import Job

# Register your models here.

# @admin.register(Job)
# class JobAdmin(admin.ModelAdmin):
#     pass

@admin.register(Dream)
class DreamAdmin(VersionAdmin):
    pass


app_models = apps.get_app_config('demo_app').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass


