from django.db import models
from solo.models import SingletonModel

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
    question_number = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Known Answer'
        verbose_name_plural = 'Known Answers'

    def __str__(self):
        return f"answer {self.pk}"

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
