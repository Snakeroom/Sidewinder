# Generated by Django 4.0.3 on 2023-07-20 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0004_increase_client_id_secret_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redditcredentials',
            name='access_token',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='redditcredentials',
            name='refresh_token',
            field=models.CharField(max_length=1000),
        ),
    ]