# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0005_auto_20150629_1536'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Alert',
            new_name='AlertSubscription',
        ),
    ]
