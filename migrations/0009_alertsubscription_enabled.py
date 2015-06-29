# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0008_auto_20150629_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertsubscription',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
    ]
