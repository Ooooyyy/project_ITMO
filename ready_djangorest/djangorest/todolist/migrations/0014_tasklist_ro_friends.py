# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-02 21:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('todolist', '0013_auto_20170530_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklist',
            name='ro_friends',
            field=models.ManyToManyField(related_name='tasklists_ro', to=settings.AUTH_USER_MODEL),
        ),
    ]
