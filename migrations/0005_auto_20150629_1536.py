# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0004_auto_20150629_0915'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('channel', models.CharField(max_length=80, choices=[['email', 'E-Mail'], ['telegram', 'Telegram Bot']])),
                ('destination', models.CharField(max_length=250)),
            ],
        ),
        migrations.AlterField(
            model_name='cam',
            name='on_event_script',
            field=models.CharField(max_length=200, default='/etc/motion/on_event_webhook.py'),
        ),
    ]
