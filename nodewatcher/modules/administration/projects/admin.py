from django.contrib import admin

from leaflet import admin as leaflet_admin

from nodewatcher.core import models as core_models


from . import models


class SSIDAdmin(admin.ModelAdmin):
    pass


class ProjectAdmin(leaflet_admin.LeafletGeoAdmin):
    list_display = ('name', 'is_default', )

    def get_nodes_entry(self, project, node):
        return {
            'node': node,
        }

    def get_nodes(self, object_id):
        project = models.Project.objects.get(pk=object_id)
        return (self.get_nodes_entry(project, node) for node in core_models.Node.objects.regpoint('config').registry_filter(core_project__project=project))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['nodes'] = self.get_nodes(object_id)
        return super(ProjectAdmin, self).change_view(request, object_id, form_url, extra_context)


admin.site.register(models.SSID, SSIDAdmin)
admin.site.register(models.Project, ProjectAdmin)
