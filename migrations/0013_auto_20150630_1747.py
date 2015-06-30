# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0012_alertsubscription_mute'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alertsubscription',
            old_name='mute',
            new_name='pause',
        ),
    ]
