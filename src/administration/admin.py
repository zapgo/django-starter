from django import forms
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.models import FlatPage

admin.site.unregister(FlatPage)
admin.site.register(ContentType)
admin.site.register(Permission)


class FlatPageAdminForm(FlatpageForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FlatPage
        fields = '__all__'

@admin.register(FlatPage)
class MyFlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm


# @admin.register(ContentType)
# class ContentTypeAdmin(admin.ModelAdmin):
#     pass
