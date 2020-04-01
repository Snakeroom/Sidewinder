from django.db import models


class KnownAnswer(models.Model):
    message = models.CharField(max_length=300, unique=True)
    correct = models.BooleanField()
    seen_times = models.PositiveIntegerField(verbose_name='times seen', default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Known Answer'
        verbose_name_plural = 'Known Answers'

    def __str__(self):
        return f"answer {self.pk}"
