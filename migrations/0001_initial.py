# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('slug', models.CharField(max_length=100, null=True, blank=True)),
                ('thread_number', models.IntegerField(null=True, blank=True)),
                ('output_pictures', models.BooleanField(default=True)),
                ('online', models.BooleanField(default=True))
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ConfigValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=255)),
                ('cam', models.ForeignKey(to='motioncontrol.Cam')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField()),
                ('event_type', models.IntegerField()),
                ('filename', models.CharField(max_length=250)),
                ('cam', models.ForeignKey(to='motioncontrol.Cam')),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('admin_url', models.CharField(default=b'http://127.0.0.1:8000/', unique=True, max_length=200)),
                ('config_folder', models.CharField(max_length=200, null=True, blank=True)),
                ('local_data_folder', models.CharField(max_length=200, null=True, blank=True)),
                ('remote_data_folder', models.CharField(help_text=b'Use if motion server on different system', max_length=200, null=True, blank=True)),
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
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('cam', 'filename')]),
        ),
    ]
