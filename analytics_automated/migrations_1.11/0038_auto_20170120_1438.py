# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-20 14:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0037_auto_20170113_1530'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='no_outputs_behaviour',
            new_name='incomplete_outputs_behaviour',
        ),
    ]
