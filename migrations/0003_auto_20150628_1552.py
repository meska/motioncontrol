# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0002_auto_20150628_1309'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='config_folder',
        ),
        migrations.AddField(
            model_name='server',
            name='local_config_folder',
            field=models.CharField(help_text=b'On motion server', max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='server',
            name='remote_config_folder',
            field=models.CharField(help_text=b'On Django server', max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='local_data_folder',
            field=models.CharField(help_text=b'On motion server', max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='remote_data_folder',
            field=models.CharField(help_text=b'On Django server', max_length=200, null=True, blank=True),
        ),
    ]
