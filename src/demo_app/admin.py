from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin
from mptt.admin import MPTTModelAdmin
from mptt.forms import MPTTAdminForm
from feincms.admin.tree_editor import TreeEditor
from .models import Dream, Thing, SubThing, SubThingFiltered


class FeinCMSModelAdmin(TreeEditor):
    """
    A ModelAdmin to add changelist tree view and editing capabilities.
    Requires FeinCMS to be installed.
    """

    form = MPTTAdminForm

    def _actions_column(self, obj):
        actions = []  # super(FeinCMSModelAdmin, self)._actions_column(obj)
        glyph_template = '<span class="glyphicon glyphicon-{icon}" aria-hidden="true"></span>'

        if hasattr(obj, 'get_absolute_url'):
            actions.append('&nbsp; <a href="%s" title="%s" target="_blank">%s</a>' % (
                obj.get_absolute_url(), _('View item'), glyph_template.format(icon='search')))

        actions.append('&nbsp; <a href="add/?%s=%s" title="%s">%s</a>' % (
            self.model._mptt_meta.parent_attr, obj.pk, _('Add child'), glyph_template.format(icon='plus')))

        actions.append(
            '&nbsp; <a><div class="drag_handle" style="background: inherit;">%s</div></a>' % glyph_template.format(
                icon='move'))

        return actions

    def delete_selected_tree(self, modeladmin, request, queryset):
        """
        Deletes multiple instances and makes sure the MPTT fields get recalculated properly.
        (Because merely doing a bulk delete doesn't trigger the post_delete hooks.)
        """
        n = 0
        for obj in queryset:
            obj.delete()
            n += 1
        self.message_user(request, _("Successfully deleted %s items.") % n)

    def get_actions(self, request):
        actions = super(FeinCMSModelAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                self.delete_selected_tree, 'delete_selected', _("Delete selected %(verbose_name_plural)s"))
        return actions


class CustomMPTTModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20


@admin.register(Thing, SubThing)
class ThingAdmin(FeinCMSModelAdmin):
    list_display = ['__str__', 'link_type']
    list_filter = ['link_type']
    mptt_level_indent = 40


@admin.register(SubThingFiltered)
class SubThingFilteredAdmin(admin.ModelAdmin):
    # list_display = ['name']
    # list_editable = ['unit_cost']

    readonly_fields = ['name', ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, **kwargs):
        return False

    # def get_queryset(self, request):
    #     return self.model.objects.filter(assessment=request.session.get('assessment_id', 1))



@admin.register(Dream)
class DreamAdmin(VersionAdmin):
    pass


app_models = apps.get_app_config('demo_app').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass


