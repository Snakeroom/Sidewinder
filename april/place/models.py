import struct
import uuid

from django.contrib import admin
from django.db import models
from django.db.models import Q
from solo.models import SingletonModel

from sidewinder.identity.models import User

PALETTE = [
    0xff4500,
    0xffa800,
    0xffd635,
    0x00a368,
    0x7eed56,
    0x2450a4,
    0x3690ea,
    0x51e9f4,
    0x811e9f,
    0xb44ac0,
    0xff99aa,
    0x9c6926,
    0x000000,
    0x898d90,
    0xd4d7d9,
    0xffffff,
    0xbe0039,
    0x00cc78,
    0x00756f,
    0x009eaa,
    0x493ac1,
    0x6a5cff,
    0xff3881,
    0x6d482f,
]


class CanvasSettings(SingletonModel):
    canvas_width = models.IntegerField(default=1000)
    canvas_height = models.IntegerField(default=1000)

    def __str__(self):
        return "Canvas Settings"

    class Meta:
        verbose_name = "Canvas Settings"


class ProjectRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    role = models.CharField(max_length=7, choices=[('owner', 'Owner'), ('manager', 'Manager'), ('user', 'User')],
                            default='user')

    def __str__(self):
        return f"{self.project} - {self.user} - {self.role}"

    class Meta:
        unique_together = ['user', 'project']


class Project(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    users = models.ManyToManyField(User, related_name='place_projects', through=ProjectRole, blank=True)
    high_priority = models.BooleanField(
        verbose_name='Featured Project',
        help_text='Gives the project special priority - shown to unauthenticated users, '
                  'has a higher chance of being picked',
        default=False
    )

    show_user_count = models.BooleanField(verbose_name='Show User Count',
                                          help_text='Whether to publicly show the '
                                                    'number of users joined to this '
                                                    'project',
                                          default=True)
    approved = models.BooleanField(help_text="Project approved by admin", default=False)

    def __str__(self):
        return self.name

    def get_user_count(self):
        return self.users.count()

    def user_is_member(self, user):
        return self.users.contains(user)

    def user_is_manager(self, user):
        if user.is_staff:
            return True

        try:
            role = ProjectRole.objects.get(user=user, project=self)
            return role.role in ('manager', 'owner')
        except ProjectRole.DoesNotExist:
            return False


def default_division_bytes():
    # pos 0, 0; size 0, 0; no data
    return b"\x00\x00\x00\x00\x00\x00\x00\x00"


class ProjectDivision(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    division_name = models.CharField(max_length=256, default="Default")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    priority = models.IntegerField(help_text="A higher number receives priority")
    enabled = models.BooleanField(help_text="Disable divisions to stop directing users to contribute to them",
                                  default=True)
    content = models.BinaryField(help_text="Image data", editable=False, default=default_division_bytes)

    # content is big-endian 4 shorts header followed by bytearray of data

    def __str__(self):
        return f"{self.project.name} - {self.division_name}"

    def unpack_header(self):
        return struct.unpack(">HHHH", self.content[:8])

    @admin.display(description="Origin")
    def get_origin(self) -> (int, int):
        """
        Get the origin of this layer
        :return: Position tuple (x, y)
        """
        pos = self.unpack_header()[:2]
        return pos[0], pos[1]

    @admin.display(description="Dimensions")
    def get_dimensions(self) -> (int, int):
        """
        Get the size of this layer
        :return: Size tuple (width, height)
        """
        size = self.unpack_header()[2:]
        return size[0], size[1]

    def get_image_bytes(self) -> bytes:
        return bytes(self.content[8:])

    def count_image_pixels(self) -> int:
        img = self.get_image_bytes()
        width, height = self.get_dimensions()

        count = 0
        for i in range(0, width * height):
            if img[i] != 0xFF:
                count += 1

        return count
