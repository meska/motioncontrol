# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0009_alertsubscription_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertsubscription',
            name='sent',
            field=models.BooleanField(default=False),
        ),
    ]
