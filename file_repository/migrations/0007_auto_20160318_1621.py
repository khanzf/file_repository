# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-18 16:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_repository', '0006_auto_20160318_0254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inode',
            name='parent',
        ),
        migrations.AlterField(
            model_name='inode',
            name='inodes',
            field=models.ManyToManyField(to='file_repository.Inode'),
        ),
    ]