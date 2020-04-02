# Generated by Django 3.0.4 on 2020-04-02 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sneknet', '0003_token_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='MasterSwitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enable_all', models.BooleanField(default=True)),
                ('enable_queries', models.BooleanField(default=True)),
                ('question_number', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Master Switches',
                'verbose_name_plural': 'Master Switches',
            },
        ),
    ]