from django.contrib import admin

from .models import Project, ProjectDivision

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'high_priority',)
    list_filter = ('high_priority',)

@admin.register(ProjectDivision)
class ProjectDivisionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'priority',)
