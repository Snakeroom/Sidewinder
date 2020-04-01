from django.contrib import admin

from april.imposter.models import KnownAnswer


@admin.register(KnownAnswer)
class KnownAnswerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'message', 'correct', 'seen_times', 'updated_at',)
    search_fields = ('message',)
    list_filter = ('correct',)
