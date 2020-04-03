from django.contrib import admin

from april.imposter.models import KnownAnswer
from sidewinder.identity.models import User


@admin.register(KnownAnswer)
class KnownAnswerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'message', 'correct', 'seen_times', 'updated_at',)
    search_fields = ('message',)
    list_filter = ('correct',)
    search_description = "You can search for specific tags by prepending 'tag:' to your search query. " \
                         "For example: 'tag:mytag'"

    def get_search_results(self, request, queryset, search_term):
        if search_term.startswith('tag:'):
            _, tag = search_term.split(':')

            return queryset.filter(submission_tag=tag), False
        elif search_term.startswith('submitter:'):
            _, name = search_term.split(':')

            try:
                user = User.objects.get(username__iexact=name)
                return queryset.filter(submitted_by=user), False
            except User.DoesNotExist:
                pass

        return super().get_search_results(request, queryset, search_term)
