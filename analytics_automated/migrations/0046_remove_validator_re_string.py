# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 15:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0045_auto_20170224_1527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='validator',
            name='re_string',
        ),
    ]
