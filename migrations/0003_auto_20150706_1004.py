# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motioncontrol', '0002_cam_thresold'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cam',
            old_name='thresold',
            new_name='threshold',
        ),
    ]
