# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-30 15:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todolist', '0004_auto_20170426_0040'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='name',
            new_name='tag',
        ),
    ]
