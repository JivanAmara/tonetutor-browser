# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-23 23:14
from __future__ import unicode_literals
import os
from django.db import migrations
from django.core.management import call_command

fixture_path = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, 'fixtures/sites_data.json')
)
def load_sites_data(aps, schema_editor):
    call_command('loaddata', fixture_path)

class Migration(migrations.Migration):

    dependencies = [
        ('tonetutor', '0003_auto_20160923_2314'),
    ]

    operations = [
        migrations.RunPython(load_sites_data)
    ]
