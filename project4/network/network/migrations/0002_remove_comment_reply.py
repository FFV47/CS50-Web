# Generated by Django 4.0.3 on 2022-03-29 03:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='reply',
        ),
    ]
