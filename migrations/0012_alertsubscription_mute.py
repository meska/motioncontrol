# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0011_server_stream_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertsubscription',
            name='mute',
            field=models.BooleanField(default=False),
        ),
    ]
