from django.contrib import admin

from .models import Project, ProjectDivision


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'featured', 'approved')
    list_filter = ('featured',)


@admin.register(ProjectDivision)
class ProjectDivisionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'priority', 'enabled')
