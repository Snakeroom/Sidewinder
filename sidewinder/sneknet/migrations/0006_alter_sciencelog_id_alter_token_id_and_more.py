# Generated by Django 4.0.3 on 2022-03-27 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sneknet', '0005_userscript'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sciencelog',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='token',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='userscript',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
