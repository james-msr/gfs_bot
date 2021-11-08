from django.db import models
from datetime import datetime



class User(models.Model):
    TYPES = [
        ('client', 'Клиент'),
        ('driver', 'Водитель')
    ]
    user_type = models.CharField('Тип пользователя', max_length=100, choices=TYPES)
    name = models.CharField('Имя клиента', max_length=100)
    phone_num = models.CharField('Номер телефона', max_length=16)
    car_num = models.CharField('Номер машины', max_length=50, blank=True, null=True)
    chat_id = models.IntegerField('ID чата', blank=True, null=True)

    def get_orders(self):
        return self.client_set.all()

    def __str__(self):
        return self.name


class Order(models.Model):
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='clients',related_query_name='client', limit_choices_to={'user_type': 'client'})
    driver = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='drivers', related_query_name='driver', limit_choices_to={'user_type': 'driver'})
    _from = models.CharField('Откуда', max_length=100)
    _to = models.CharField('Куда', max_length=100)
    latitude = models.FloatField('Долгота', max_length=100, null=True, blank=True)
    longitude = models.FloatField('Широта', max_length=100, null=True, blank=True)
    last_update = models.DateTimeField('Последнее обновление', null=True, blank=True)

    def get_route(self):
        return self._from + ' - ' + self._to

    def update_time(self):
        self.last_update = datetime.now()
        return self.last_update

    def __str__(self):
        return self.client.name