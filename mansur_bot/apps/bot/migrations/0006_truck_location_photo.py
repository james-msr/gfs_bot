# Generated by Django 3.2.4 on 2021-11-03 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_remove_truck_location_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='truck',
            name='location_photo',
            field=models.ImageField(default=0, upload_to='', verbose_name='Фото локации'),
            preserve_default=False,
        ),
    ]