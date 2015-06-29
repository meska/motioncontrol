# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0006_auto_20150629_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertsubscription',
            name='alert_from',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alertsubscription',
            name='alert_motion',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alertsubscription',
            name='alert_nomotion',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alertsubscription',
            name='alert_nomotion_length',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alertsubscription',
            name='alert_to',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alertsubscription',
            name='cam',
            field=models.ForeignKey(to='motioncontrol.Cam', default=0),
            preserve_default=False,
        ),
    ]
