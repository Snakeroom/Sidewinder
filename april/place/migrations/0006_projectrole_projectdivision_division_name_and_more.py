# Generated by Django 4.0.3 on 2023-03-18 20:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('identity', '0004_increase_client_id_secret_length'),
        ('place', '0005_canvassettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectdivision',
            name='division_name',
            field=models.CharField(default='Default', max_length=256),
        ),
        migrations.AlterField(
            model_name='projectdivision',
            name='priority',
            field=models.IntegerField(help_text='A higher number receives priority'),
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE place_project_users RENAME TO place_projectrole',
                    reverse_sql='ALTER TABLE place_projectrole RENAME TO place_project_users',
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='ProjectRole',
                    fields=[
                        ('id',
                         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('user',
                         models.ForeignKey(on_delete=models.CASCADE, to='identity.User')),
                        ('project',
                         models.ForeignKey(on_delete=models.CASCADE, to='place.Project')),
                    ],
                ),
                migrations.AlterField(
                    model_name='project',
                    name='users',
                    field=models.ManyToManyField(blank=True, related_name='place_projects', through='place.ProjectRole',
                                                 to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.AddField(
            model_name='projectrole',
            name='role',
            field=models.CharField(choices=[('owner', 'Owner'), ('manager', 'Manager'), ('user', 'User')],
                                   default='user', max_length=7),
        ),
        migrations.AlterUniqueTogether(
            name='projectrole',
            unique_together={('user', 'project')},
        ),
    ]
