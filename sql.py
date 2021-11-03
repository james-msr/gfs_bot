import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mansur_bot.settings")
django.setup()

from bot.models import Client, Route

from asgiref.sync import sync_to_async

class SQL_handler():

    def get_client(self, phone):
        return Client.objects.get(phone_num=phone)

    async def get_client_routes(self, client):
        return await sync_to_async(list)(client.route.all())

    async def get_clients(self):
        return await sync_to_async(list)(Client.objects.all())

    async def get_routes(self):
        return await sync_to_async(list)(Route.objects.all())

a = Client.objects.get(id=1)
print(a.route.all())