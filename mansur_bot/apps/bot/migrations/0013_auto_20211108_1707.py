# Generated by Django 3.2.4 on 2021-11-08 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0012_auto_20211108_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='latitude',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Долгота'),
        ),
        migrations.AlterField(
            model_name='order',
            name='longitude',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Широта'),
        ),
    ]
