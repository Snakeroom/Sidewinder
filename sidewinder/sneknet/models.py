from django.db import models

class ScienceLog(models.Model):
    user_hash = models.CharField(max_length=100)
    total_actions = models.IntegerField()

    class Meta:
        verbose_name = 'science log'
        verbose_name_plural = 'science logs'

    def __str__(self):
        return self.user_hash
