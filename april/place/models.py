from django.db import models
from sidewinder.identity.models import User

import uuid

class Project(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    users = models.ManyToManyField(User, related_name='place_projects', blank=True)
    high_priority = models.BooleanField(verbose_name='High Priority', help_text='Gives the project special priority - '
                                        'shown to unauthenticated users, has a higher chance of being picked')

    def __str__(self):
        return self.name

class ProjectDivision(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    priority = models.IntegerField(help_text="Lower is better")

    def __str__(self):
        return f"{self.project.name} - {self.uuid}"
