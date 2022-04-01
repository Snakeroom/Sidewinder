from django.db import models
from sidewinder.identity.models import User

import struct
import uuid

class Project(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    users = models.ManyToManyField(User, related_name='place_projects', blank=True)
    high_priority = models.BooleanField(
        verbose_name='Featured Project',
        help_text='Gives the project special priority - shown to unauthenticated users, '
                  'has a higher chance of being picked',
        default=False
    )

    show_user_count = models.BooleanField(verbose_name='Show User Count', help_text='Whether to publicly show the '
                                          'number of users joined to this project', default=True)
    approved = models.BooleanField(help_text="Project approved by admin", default=False)

    def __str__(self):
        return self.name

def default_division_bytes():
    # pos 0, 0; size 0, 0; no data
    return b"\x00\x00\x00\x00\x00\x00\x00\x00"

class ProjectDivision(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    priority = models.IntegerField(help_text="Higher is better")
    enabled = models.BooleanField(help_text="Disable divisions to stop directing users to contribute to them", default=True)
    content = models.BinaryField(help_text="Image data", editable=False, default=default_division_bytes)

    # content is big-endian 4 shorts header followed by bytearray of data

    def __str__(self):
        return f"{self.project.name} - {self.uuid}"

    def unpack_header(self):
        return struct.unpack(">HHHH", self.content)

    def get_origin(self) -> (int, int):
        """
        Get the origin of this layer
        :return: Position tuple (x, y)
        """
        pos = self.unpack_header()[:2]
        return pos[0], pos[1]

    def get_dimensions(self) -> (int, int):
        """
        Get the size of this layer
        :return: Size tuple (width, height)
        """
        size = self.unpack_header()[2:]
        return size[0], size[1]

    def get_image_bytes(self) -> bytes:
        return self.content[4:]
