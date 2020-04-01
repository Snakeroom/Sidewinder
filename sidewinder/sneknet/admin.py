from django.contrib import admin

from sidewinder.sneknet.models import ScienceLog


@admin.register(ScienceLog)
class ScienceLogAdmin(admin.ModelAdmin):
    list_display = ('user_hash', 'total_actions',)

