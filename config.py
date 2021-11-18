from aiogram import Dispatcher, Bot, executor, types

from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging

# Install django
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mansur_bot.settings")
django.setup()

# Configure bot
BOT_TOKEN = '2035003130:AAHXsox9UbKrC6c8xT8B8V72G7nYayWoj7o'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)
