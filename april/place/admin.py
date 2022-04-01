from django.contrib import admin

from .models import Project, ProjectDivision


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'high_priority', 'approved')
    list_filter = ('high_priority', 'approved')


@admin.register(ProjectDivision)
class ProjectDivisionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'priority', 'enabled', 'get_origin', 'get_dimensions',)
    readonly_fields = ('get_origin', 'get_dimensions',)
