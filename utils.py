from config import *
import datetime

from bot.models import User, Order

def user_exists(id=None, phone=None):
    if User.objects.filter(chat_id=id).exists() or User.objects.filter(phone_num=phone).exists():
        return True
    else:
        return False


def is_client(id):
    user = User.objects.get(chat_id=id)
    if user.user_type == 'client':
        return True
    else:
        return False


async def client_commands():
    bot_commands = [
        types.BotCommand(command="active", description="Активные маршруты"),
        types.BotCommand(command="finished", description="Оконченные маршруты")
    ]
    await bot.set_my_commands(bot_commands)

def date_valid(date):
    format = "%Y-%m-%d"

    try:
        datetime.datetime.strptime(date, format)
        return True
    except ValueError:
        return False
