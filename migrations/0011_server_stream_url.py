# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0010_alertsubscription_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='stream_url',
            field=models.CharField(unique=True, default='http://127.0.0.1/', help_text='Stream base url, requires nginx configuration', max_length=200),
        ),
    ]
