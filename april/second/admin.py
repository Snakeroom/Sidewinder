from django.contrib import admin

from april.second.models import UserPreference

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'prefer_streaks',)
