# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0007_auto_20150629_1548'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='alertsubscription',
            unique_together=set([('channel', 'destination', 'cam', 'alert_motion', 'alert_nomotion')]),
        ),
    ]
