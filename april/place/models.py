import uuid

import numpy as np
from PIL import Image
from django.contrib import admin
from django.db import models
from solo.models import SingletonModel

from april.place.views import get_canvas_config
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
    return


class ProjectDivision(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='UUID')
    division_name = models.CharField(max_length=256, default="Default")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    priority = models.IntegerField(help_text="A higher number receives priority")
    enabled = models.BooleanField(help_text="Disable divisions to stop directing users to contribute to them",
                                  default=True)
    height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    origin_x = models.IntegerField(default=0, verbose_name='Origin X')
    origin_y = models.IntegerField(default=0, verbose_name='Origin Y')

    def __str__(self):
        return f"{self.project.name} - {self.division_name}"

    @admin.display(description="Origin")
    def get_origin(self) -> (int, int):
        """
        Get the origin of this layer
        :return: Position tuple (x, y)
        """
        settings = get_canvas_config()
        return settings.canvas_offset_x - self.origin_x, settings.canvas_offset_y - self.origin_y

    @admin.display(description="Dimensions")
    def get_dimensions(self):
        """
        Get the bitmap size for this division
        :return: Size tuple (width, height)
        """
        if hasattr(self, 'image'):
            return self.image.width, self.image.height
        else:
            return None, None

    def get_image(self):
        """
        Get the bitmap for this division
        :return: Image numpy.ndarray
        """
        if hasattr(self, 'image'):
            image = np.asarray(Image.open(self.image.image.path).convert('RGBA'))
            return image
        else:
            return None

    @admin.display(description='Pixel Count')
    def get_pixel_count(self):
        """
        Get a count of pixels in this division
        :return: Count int
        """
        img = self.get_image()
        if img is None:
            return None
        else:
            return np.count_nonzero(
                img[..., -1] != 0)  # TODO Determine if pixels should be counted with full or any opacity

    def image_path(self) -> str:
        return f'y22/bitmaps/{self.uuid}/{self.project.uuid}.png'


def image_path(self, _) -> str:
    """
    Return path to store bitmap image
    :param self:
    :param _: Original filename of image
    :return: Path str
    """
    return self.project_division.image_path()

class ProjectDivisionImage(models.Model):
    project_division = models.OneToOneField(ProjectDivision, on_delete=models.DO_NOTHING, related_name='image',
                                            editable=False)
    image = models.ImageField(width_field='width', height_field='height',
                              upload_to=image_path, null=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
