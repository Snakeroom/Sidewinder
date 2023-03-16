from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Project, ProjectDivision, CanvasSettings, ProjectRole

admin.site.register(CanvasSettings, SingletonModelAdmin)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'high_priority', 'approved')
    list_filter = ('high_priority', 'approved')


@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role')
    list_filter = ('project', 'role')


@admin.register(ProjectDivision)
class ProjectDivisionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'priority', 'enabled', 'get_origin', 'get_dimensions')
    readonly_fields = ('get_origin', 'get_dimensions')
