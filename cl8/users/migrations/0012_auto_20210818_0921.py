# Generated by Django 3.0.7 on 2021-08-18 09:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20210818_0854'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='_photo_thumbbail_url',
            new_name='_photo_thumbnail_url',
        ),
    ]
