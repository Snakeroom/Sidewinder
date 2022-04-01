# Generated by Django 4.0.3 on 2022-04-01 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('place', '0003_projectdivision_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='approved',
            field=models.BooleanField(default=False, help_text='Project approved by admin'),
        ),
        migrations.AddField(
            model_name='projectdivision',
            name='enabled',
            field=models.BooleanField(default=True, help_text='Disable divisions to stop directing users to contribute to them'),
        ),
        migrations.AlterField(
            model_name='project',
            name='high_priority',
            field=models.BooleanField(default=False, help_text='Gives the project special priority - shown to unauthenticated users, has a higher chance of being picked', verbose_name='Featured Project'),
        ),
        migrations.AlterField(
            model_name='projectdivision',
            name='priority',
            field=models.IntegerField(help_text='Higher is better'),
        ),
    ]
