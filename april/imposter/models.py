from django.db import models

from sidewinder.identity.models import User


class KnownAnswer(models.Model):
    message = models.CharField(max_length=300, unique=True)
    correct = models.BooleanField()
    seen_times = models.PositiveIntegerField(verbose_name='times seen', default=0)

    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='submitted_answers',
                                     null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submission_tag = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        verbose_name = 'Known Answer'
        verbose_name_plural = 'Known Answers'

    def __str__(self):
        return f"answer {self.pk}"
