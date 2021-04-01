from django.core.exceptions import ValidationError
from django.db import models

from sidewinder.identity.models import User

import re

SEMVER_REGEX = re.compile(r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>("
                          r"?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-]["
                          r"0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")

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

def semver_validator(entry):
    if SEMVER_REGEX.match(entry) is None:
        raise ValidationError("Version is not a valid semantic version string")

class UserScript(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField()
    location = models.URLField(max_length=512)
    version = models.CharField(max_length=64, validators=[semver_validator])
    recommended = models.BooleanField(default=False, help_text="Whether to promote this script.")
    force_disable = models.BooleanField(default=False, verbose_name="Force disable",
                                        help_text="Force-disable this script for all users.")

    def __str__(self):
        return self.name
