from django import forms
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget

from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.models import FlatPage

admin.site.unregister(FlatPage)


class FlatPageAdminForm(FlatpageForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FlatPage
        fields = '__all__'


@admin.register(FlatPage)
class MyFlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm


# admin.site.register(FlatPage, MyFlatPageAdmin)
