from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

from reversion.admin import VersionAdmin
from .models import Dream

# Register your models here.

@admin.register(Dream)
class DreamAdmin(VersionAdmin):
    pass


app_models = apps.get_app_config('version_demo').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
