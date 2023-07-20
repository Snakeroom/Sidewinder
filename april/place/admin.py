from django.contrib import admin
from solo.admin import SingletonModelAdmin
from image_uploader_widget.admin import ImageUploaderInline

from .models import Project, ProjectDivision, ProjectDivisionImage, CanvasSettings, ProjectRole

admin.site.register(CanvasSettings, SingletonModelAdmin)


# TODO: Optimize the foreignkey field in here. Should be possible to prefetch but
#       will require some hackery
class ProjectRoleAdmin(admin.TabularInline):
    model = ProjectRole
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'high_priority', 'approved')
    list_filter = ('high_priority', 'approved')
    inlines = (ProjectRoleAdmin,)
    filter_horizontal = ('users',)


class BitmapWidgetAdmin(ImageUploaderInline):
    model = ProjectDivisionImage


@admin.register(ProjectDivision)
class ProjectDivisionAdmin(admin.ModelAdmin):
    inlines = (BitmapWidgetAdmin,)
    list_display = ('__str__', 'priority', 'enabled', 'get_origin', 'get_dimensions')
    readonly_fields = ('uuid', 'get_dimensions', 'get_pixel_count')
