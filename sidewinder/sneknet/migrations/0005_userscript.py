# Generated by Django 3.0.4 on 2021-04-01 23:05

from django.db import migrations, models
import sidewinder.sneknet.models


class Migration(migrations.Migration):

    dependencies = [
        ('sneknet', '0004_skip_moved_masterswitch'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserScript',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField()),
                ('location', models.URLField(max_length=512)),
                ('version', models.CharField(max_length=64, validators=[sidewinder.sneknet.models.semver_validator])),
                ('recommended', models.BooleanField(default=False, help_text='Whether to promote this script.')),
                ('force_disable', models.BooleanField(default=False, help_text='Force-disable this script for all users.', verbose_name='Force disable')),
            ],
        ),
    ]
