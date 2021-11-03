# Generated by Django 3.2.4 on 2021-11-03 10:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20211101_1659'),
    ]

    operations = [
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.CharField(max_length=20, verbose_name='Номер машины')),
                ('location_photo', models.ImageField(upload_to='', verbose_name='Фото локации')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bot.client')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bot.route')),
            ],
        ),
    ]