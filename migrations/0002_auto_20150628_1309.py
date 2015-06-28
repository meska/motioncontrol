# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cam',
            name='lastmotion',
        ),
        migrations.AddField(
            model_name='cam',
            name='last_event',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
