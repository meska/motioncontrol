# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AlertSubscription',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('channel', models.CharField(max_length=80, choices=[['email', 'E-Mail'], ['telegram', 'Telegram Bot']])),
                ('destination', models.CharField(max_length=250)),
                ('alert_motion', models.BooleanField(default=False)),
                ('alert_nomotion', models.BooleanField(default=False)),
                ('alert_nomotion_length', models.TimeField(null=True, blank=True)),
                ('alert_from', models.DateTimeField(null=True, blank=True)),
                ('alert_to', models.DateTimeField(null=True, blank=True)),
                ('enabled', models.BooleanField(default=False)),
                ('sent', models.BooleanField(default=False)),
                ('pause', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Cam',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('slug', models.CharField(max_length=100, null=True, blank=True)),
                ('thread_number', models.IntegerField(null=True, blank=True)),
                ('output_pictures', models.BooleanField(default=True)),
                ('online', models.BooleanField(default=True)),
                ('last_event', models.DateTimeField(null=True, blank=True)),
                ('on_event_script', models.CharField(max_length=200, default='/etc/motion/on_event_webhook.py')),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ConfigValue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=255)),
                ('cam', models.ForeignKey(to='motioncontrol.Cam')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('datetime', models.DateTimeField()),
                ('event_type', models.IntegerField()),
                ('filename', models.CharField(max_length=250)),
                ('cam', models.ForeignKey(to='motioncontrol.Cam')),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('admin_url', models.CharField(unique=True, max_length=200, default='http://127.0.0.1:8000/')),
                ('stream_url', models.CharField(unique=True, max_length=200, help_text='Stream base url, requires nginx configuration', default='http://127.0.0.1/')),
                ('local_config_folder', models.CharField(max_length=200, null=True, blank=True, help_text='On motion server')),
                ('local_data_folder', models.CharField(max_length=200, null=True, blank=True, help_text='On motion server')),
                ('remote_config_folder', models.CharField(max_length=200, null=True, blank=True, help_text='On Django server')),
                ('remote_data_folder', models.CharField(max_length=200, null=True, blank=True, help_text='On Django server')),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='cam',
            name='server',
            field=models.ForeignKey(to='motioncontrol.Server'),
        ),
        migrations.AddField(
            model_name='alertsubscription',
            name='cam',
            field=models.ForeignKey(to='motioncontrol.Cam'),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('cam', 'filename')]),
        ),
        migrations.AlterUniqueTogether(
            name='alertsubscription',
            unique_together=set([('channel', 'destination', 'cam', 'alert_motion', 'alert_nomotion')]),
        ),
    ]
