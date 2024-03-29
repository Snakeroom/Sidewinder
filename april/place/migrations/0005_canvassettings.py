# Generated by Django 4.0.3 on 2022-04-02 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('place', '0004_project_approved_projectdivision_enabled_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CanvasSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canvas_width', models.IntegerField(default=1000)),
                ('canvas_height', models.IntegerField(default=1000)),
            ],
            options={
                'verbose_name': 'Canvas Settings',
            },
        ),
    ]
