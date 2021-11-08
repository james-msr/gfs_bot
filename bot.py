import asyncio
import aioschedule
import logging


from aiogram import Dispatcher, Bot, executor, types
from aiogram.utils.callback_data import CallbackData
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import Message

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mansur_bot.settings")
django.setup()

from bot.models import User, Order

from asgiref.sync import sync_to_async
print(User.objects.filter(user_type='driver'))

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
        phonenumber= str(message.contact.phone_number)
        print(phonenumber)
        # try:
        user = await sync_to_async(User.objects.get)(phone_num=phonenumber)
        user.chat_id = message.chat.id
        await sync_to_async(user.save)()
        if user.user_type == 'client':
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_routes = types.KeyboardButton(text="Маршруты")
            keyboard.add(button_routes)
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_location = types.KeyboardButton(text="Отправить локацию", request_location=True)
            keyboard.add(button_location)
        await bot.send_message(message.chat.id, 'Выберите опцию', reply_markup=keyboard)
        # except:
        #     await bot.send_message(message.chat.id, 'Отправьте свой номер')
            
    
@dp.message_handler(content_types=['text'])
async def send_routes(message: Message):
    if message.text == 'Маршруты':
        user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
        orders = await sync_to_async(list)(Order.objects.filter(client=user))
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        for order in orders:
            order_name = await sync_to_async(order.get_route)()
            button = types.InlineKeyboardButton(order_name, callback_data=route_cb.new(action='order_btn', id=order.id))
            keyboard.add(button)
        await bot.send_message(message.chat.id, "Маршруты", reply_markup=keyboard)


@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
    lat = message.location.latitude
    lon = message.location.longitude
    order = await sync_to_async(Order.objects.get)(driver=user)
    order.latitude = lat
    order.longitude = lon
    await sync_to_async(order.save)()
    await message.answer('Местополежение отправлено', reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(route_cb.filter(action='order_btn'))
async def order_handler(query: CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    id = callback_data['id']
    order = await sync_to_async(Order.objects.get)(pk=id)
    await bot.send_location(query.from_user.id, order.latitude, order.longitude)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)