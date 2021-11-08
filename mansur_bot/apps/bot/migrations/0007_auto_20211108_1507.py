# Generated by Django 3.2.4 on 2021-11-08 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_truck_location_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('truck', models.CharField(max_length=20, verbose_name='Номер машины')),
                ('location_photo', models.ImageField(upload_to='', verbose_name='Фото локации')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bot.client')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bot.route')),
            ],
        ),
        migrations.DeleteModel(
            name='Truck',
        ),
    ]
