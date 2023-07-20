from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from solo.models import SingletonModel


class UserMixin(models.Model):
    is_staff = models.BooleanField(verbose_name='staff status', default=False,
                                   help_text="Designates whether the user can log into this admin site.")
    is_active = models.BooleanField(verbose_name='active', default=True,
                                    help_text="Designates whether this user should be treated as active. "
                                              "Unselect this instead of deleting accounts.")
    date_joined = models.DateTimeField(verbose_name='date joined', default=timezone.now)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, UserMixin):
    username_validator = UnicodeUsernameValidator()

    uid = models.CharField(max_length=32, primary_key=True, help_text="Reddit ID")
    username = models.CharField(max_length=100, unique=True,
                                help_text="Required. 100 characters or fewer. Letters, digits and @/./+/-/_ only.",
                                validators=[username_validator],
                                error_messages={
                                    'unique': "A user with that username already exists.",
                                })
    email = models.EmailField(verbose_name='email address', blank=True)
    pronouns = models.CharField(max_length=300, default='unspecified')

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['uid', 'email']

    objects = UserManager()

    def __str__(self):
        return self.username

class RedditApplication(SingletonModel):
    name = models.CharField(max_length=72)

    client_id = models.CharField(max_length=22)
    client_secret = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Reddit Application'
        verbose_name_plural = 'Reddit Applications'

class RedditCredentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')

    access_token = models.CharField(max_length=1000)
    refresh_token = models.CharField(max_length=1000)
    last_refresh = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - Reddit"

    class Meta:
        verbose_name = 'Reddit Credentials'
        verbose_name_plural = 'Reddit Credentials'
