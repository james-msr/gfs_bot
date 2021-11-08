# Generated by Django 3.2.4 on 2021-11-08 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_auto_20211108_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('client', 'Клиент'), ('driver', 'Водитель')], max_length=100, verbose_name='Тип пользователя'),
        ),
    ]
