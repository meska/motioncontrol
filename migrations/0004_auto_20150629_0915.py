# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0003_auto_20150628_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='cam',
            name='on_event_script',
            field=models.CharField(max_length=200, default='/etc/motion/on_event.py'),
        ),
        migrations.AlterField(
            model_name='server',
            name='admin_url',
            field=models.CharField(max_length=200, unique=True, default='http://127.0.0.1:8000/'),
        ),
        migrations.AlterField(
            model_name='server',
            name='local_config_folder',
            field=models.CharField(null=True, max_length=200, blank=True, help_text='On motion server'),
        ),
        migrations.AlterField(
            model_name='server',
            name='local_data_folder',
            field=models.CharField(null=True, max_length=200, blank=True, help_text='On motion server'),
        ),
        migrations.AlterField(
            model_name='server',
            name='remote_config_folder',
            field=models.CharField(null=True, max_length=200, blank=True, help_text='On Django server'),
        ),
        migrations.AlterField(
            model_name='server',
            name='remote_data_folder',
            field=models.CharField(null=True, max_length=200, blank=True, help_text='On Django server'),
        ),
    ]
