from solo.models import SingletonModel
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

class MasterSwitch(SingletonModel):
    enable_all = models.BooleanField(default=True)
    enable_queries = models.BooleanField(default=True)
    enable_imposter_flipping = models.BooleanField(
        default=True,
        help_text='Enable overwriting of imposter-tagged messages to human if we get a conflicting report'
    )
    enable_five_human_hiding = models.BooleanField(
        default=False,
        help_text='Enable to cause the /query endpoint to lie if it\'s going to return 5 incorrect answers'
    )

    disable_unauthorized_queries = models.BooleanField(
        default=False,
        help_text='Tick this box to disable any requests to /query that are missing a valid token'
    )

    question_number = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Master Switches"
        verbose_name_plural = "Master Switches"

    def __str__(self):
        return "Master Switches"
