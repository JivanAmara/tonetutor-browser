# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-12 21:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usermgmt', '0005_auto_20160912_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionhistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
