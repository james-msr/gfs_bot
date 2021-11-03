from django.db import models


class Route(models.Model):
    a_point = models.CharField('Точка A', max_length=200)
    b_point = models.CharField('Точка B', max_length=200)

    def __str__(self):
        return self.a_point + ' - ' + self.b_point


class Client(models.Model):
    route = models.ManyToManyField(Route, verbose_name='Маршрут', null=True, blank=True)
    name = models.CharField('Имя клиента', max_length=100)
    phone_num = models.CharField('Номер телефона', max_length=16)

    def __str__(self):
        return self.name


class Truck(models.Model):
    route = models.ForeignKey(Route, on_delete=models.DO_NOTHING)
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING)
    num = models.CharField('Номер машины', max_length=20)
    location_photo = models.ImageField('Фото локации')

    def __str__(self):
        return self.num