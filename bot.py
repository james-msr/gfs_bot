import asyncio
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import Message
import aioschedule
import logging
import json



from aiogram import Dispatcher, Bot, executor, types
from aiogram.utils.markdown import link
from aiogram.utils.callback_data import CallbackData

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mansur_bot.settings")
django.setup()

from bot.models import Client, Route, Truck

from asgiref.sync import sync_to_async


logging.basicConfig(level=logging.INFO)
BOT_TOKEN = '2035003130:AAHXsox9UbKrC6c8xT8B8V72G7nYayWoj7o'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

route_cb = CallbackData('route', 'action', 'id')


@dp.message_handler(commands=['start'])
async def phone(message: Message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить телефон", request_contact=True)
    keyboard.add(button_phone)
    await bot.send_message(message.chat.id, 'Номер телефона', reply_markup=keyboard)


@dp.message_handler(content_types=['contact'])
async def contact(message: Message):
    if message.contact is not None:
        keyboard2 = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, 'Вы успешно отправили свой номер', reply_markup=keyboard2)
        global phonenumber
        phonenumber= str(message.contact.phone_number)
        print(phonenumber)
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_routes = types.KeyboardButton(text="Маршруты")
        keyboard.add(button_routes)
        try:
            global client
            client = await sync_to_async(Client.objects.get)(phone_num=phonenumber)
            await bot.send_message(message.chat.id, 'Выберите опцию', reply_markup=keyboard)
        except:
            await bot.send_message(message.chat.id, 'Отправьте свой номер')
            
    


@dp.message_handler(content_types=['text'])
async def send_routes(message: Message):
    if message.text == 'Маршруты':
        routes = await sync_to_async(list)(client.route.all())
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        for route in routes:
            button = types.InlineKeyboardButton(route.__str__(), callback_data=route_cb.new(action='route_btn', id=route.id))
            keyboard.add(button)
        await bot.send_message(message.chat.id, "Маршруты", reply_markup=keyboard)


@dp.callback_query_handler(route_cb.filter(action='route_btn'))
async def vote_up_cb_handler(query: CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    id = callback_data['id']
    route = await sync_to_async(Route.objects.get)(pk=id)
    truck = await sync_to_async(Truck.objects.get)(route=route, client=client)
    photo = truck.location_photo.url
    print(photo)
    location = photo[1:]
    with open(location, 'rb') as p:
        await bot.send_photo(query.from_user.id, p, truck.num)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)