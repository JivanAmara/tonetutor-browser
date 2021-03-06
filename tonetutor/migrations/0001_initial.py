# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-13 19:40
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command

fixture = 'initial_data.json'

def load_fixture(apps, schema_editor):
    call_command('loaddata', fixture, app_label='tonetutor')


class Migration(migrations.Migration):

    dependencies = [
        ('sitetree', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]
