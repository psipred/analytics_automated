# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-13 15:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0053_auto_20171113_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='UUID',
            field=models.CharField(db_index=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='batch',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batch', to='analytics_automated.Submission', unique=True),
        ),
    ]
