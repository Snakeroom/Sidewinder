from datetime import datetime

from django.db import models
from solo.models import SingletonModel

from sidewinder.identity.models import User

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    prefer_streaks = models.BooleanField(help_text="Whether to prefer long streaks or mix.", default=False)

    def __str__(self):
        return str(self.user)

class UserState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='state')
    wins = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0, verbose_name="Current win streak")
    losses = models.IntegerField(default=0)

    last_was_win = models.BooleanField(verbose_name="Last vote was a win?", default=False)
    last_active = models.DateTimeField(default=datetime.utcfromtimestamp(0), db_index=True)
    current_channel = models.CharField(max_length=512, null=True, default=None)

    def __str__(self):
        return str(self.user)

def create_models(sender, instance, created, **kwargs):
    if created:
        UserPreference.objects.create(user=instance)
        UserState.objects.create(user=instance)

models.signals.post_save.connect(create_models, sender=User, weak=False, dispatch_uid='models.create_user_state')

class RoundState(SingletonModel):
    round_id = models.IntegerField(default=0)
    first_count = models.IntegerField(default=0)
    second_count = models.IntegerField(default=0)

    def ratio(self) -> float:
        if self.first_count == 0:
            return 1

        return self.second_count / self.first_count

    def clear(self):
        self.first_count = 0
        self.second_count = 0

    def __str__(self):
        return "Current Round State"
