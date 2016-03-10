from django import forms
from django.conf.urls import url
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _


from .views import TestView


class TPAMAdminSite(admin.AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = ugettext_lazy('Django site admin')

    # Text to put in each page's <h1>.
    site_header = ugettext_lazy('Django administration')

    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy('Site administration')

    # URL for the "View site" link at the top of each admin page.
    site_url = '/'

    def get_urls(self):
        from django.conf.urls import url

        urls = super(TPAMAdminSite, self).get_urls()
        urls += [
            url(r'^my_view/$', self.admin_view(TestView.as_view()))
        ]
        return urls

admin_site = TPAMAdminSite(name='tpam_admin')
# admin_site.register(FlatPage)

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


# admin.site.register(FlatPage, MyFlatPageAdmin)

# @admin.register(ContentType)
# class ContentTypeAdmin(admin.ModelAdmin):
#     pass
