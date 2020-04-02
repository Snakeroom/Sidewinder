from django.db import models

from sidewinder.identity.models import User

class ScienceLog(models.Model):
    user_hash = models.CharField(max_length=100)
    total_actions = models.IntegerField()

    class Meta:
        verbose_name = 'science log'
        verbose_name_plural = 'science logs'

    def __str__(self):
        return self.user_hash

class Token(models.Model):
    token = models.CharField(max_length=128, unique=True)
    active = models.BooleanField(default=True)
    friendly_name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='snek_tokens', null=True, blank=True)
    whitelisted_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.friendly_name
