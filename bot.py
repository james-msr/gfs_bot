import asyncio
import aioschedule
import logging


from aiogram import Dispatcher, Bot, executor, types
from aiogram.utils.callback_data import CallbackData
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import Message
from asgiref.sync import sync_to_async

# Install django
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mansur_bot.settings")
django.setup()

from bot.models import User, Order


logging.basicConfig(level=logging.INFO)

# Configure bot
BOT_TOKEN = '2035003130:AAHXsox9UbKrC6c8xT8B8V72G7nYayWoj7o'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

route_cb = CallbackData('route', 'action', 'id')


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


# Command handlers
# Ask phone number after command start
@dp.message_handler(commands=['start'])
async def phone(message: Message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер", request_contact=True)
    keyboard.add(button_phone)
    button_reg = types.KeyboardButton(text="Зарегистрироваться")
    keyboard.add(button_reg)
    await bot.send_message(message.chat.id, 'Отправьте номер телефона, если вы регистрированный клиент.\nПройдите регистрацию, если вы гость', reply_markup=keyboard)


@dp.message_handler(commands=['register'])
async def register(message: Message):
    if await sync_to_async(user_exists)(message.chat.id):
        if await sync_to_async(is_client)(message.chat.id):
            await bot.send_message(message.chat.id, 'Смотрю совсем ахуел регаться второй раз')
        else:
            await bot.send_message(message.chat.id, 'Ты водитель нахуй регаешься? Бесагон чесуэлла Мансур уже тебя зарегал. Сиди хуй жми')
    else:
        user = await sync_to_async(User.objects.create)()
        user.user_type = 'client'
        user.chat_id = message.chat.id
        await sync_to_async(user.save)()
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Отправить номер", request_contact=True)
        keyboard.add(button_phone)
        await bot.send_message(message.chat.id, 'Отправьте номер', reply_markup=keyboard)


@dp.message_handler(commands=['authorize'])
async def authorize(message: Message):
    if await sync_to_async(user_exists)(message.chat.id):
        if await sync_to_async(is_client)(message.chat.id):
            await bot.send_message(message.chat.id, 'Ты еблан? Ты уже авторизован долбаеб')
        else:
            await bot.send_message(message.chat.id, 'Бля эти команды нахуй не нажимай. Не для твоих мазолевых рук')
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Отправить номер", request_contact=True)
        keyboard.add(button_phone)
        await bot.send_message(message.chat.id, 'Отправьте номер', reply_markup=keyboard)


@dp.message_handler(commands=['routes'])
async def routes(message: Message):
    if await sync_to_async(user_exists)(message.chat.id):
        if await sync_to_async(is_client)(message.chat.id):
            user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
            orders = await sync_to_async(list)(Order.objects.filter(client=user))
            if orders != []:
                keyboard = types.InlineKeyboardMarkup(row_width=3)
                for order in orders:
                    order_name = await sync_to_async(order.get_route)()
                    button = types.InlineKeyboardButton(order_name, callback_data=route_cb.new(action='order_btn', id=order.id))
                    keyboard.add(button)
                await bot.send_message(message.chat.id, "Маршруты", reply_markup=keyboard)
            else:
                await bot.send_message(message.chat.id, "Нет у тя нахуй маршрутов")
        else:
            await bot.send_message(message.chat.id, "У тя один только маршрут. Перед глазами смотри")
    else:
        await bot.send_message(message.chat.id, "Сначала ебись, потом кончай, а не наоборот. Сначала регайся и авторизуйся потом уже спрашивай свои ебаные маршруты жалаб")


# Get user by phone number and match to client or driver if user is already registerd
# Save phone number of a new created user if user is registering
@dp.message_handler(content_types=['contact'])
async def contact(message: Message):
    if message.contact is not None:
        keyboard2 = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, 'Вы успешно отправили свой номер', reply_markup=keyboard2)
        if str(message.contact.phone_number)[0] == '+':
            phonenumber= str(message.contact.phone_number)[1:]
        else:
            phonenumber= str(message.contact.phone_number)
        exist = await sync_to_async(User.objects.filter)(phone_num=phonenumber)

        # If user is already registered
        if await sync_to_async(user_exists)(phone=phonenumber):
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
        
        # If user is registering
        else:
            if await sync_to_async(user_exists)(message.chat.id): 
                user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
                user.phone_num = phonenumber
                await sync_to_async(user.save)()
                await bot.send_message(message.chat.id, 'Введите свое имя')
            else:
                await bot.send_message(message.chat.id, 'Ай баран. Ты еще и не регался куда лезешь сучара?')


# For clients
# Handle text messages of the client
@dp.message_handler(content_types=['text'])
async def handle_messages(message: Message):

    # send routes of the client
    if message.text == 'Маршруты':
        user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
        orders = await sync_to_async(list)(Order.objects.filter(client=user))
        if orders != []:
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            for order in orders:
                order_name = await sync_to_async(order.get_route)()
                button = types.InlineKeyboardButton(order_name, callback_data=route_cb.new(action='order_btn', id=order.id))
                keyboard.add(button)
            await bot.send_message(message.chat.id, "Маршруты", reply_markup=keyboard)
        else:
            await bot.send_message(message.chat.id, "Нет у тя нахуй маршрутов")
        
    # register new client
    elif message.text == 'Зарегистрироваться':
        user = await sync_to_async(User.objects.create)()
        user.user_type = 'client'
        user.chat_id = message.chat.id
        await sync_to_async(user.save)()
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Отправить номер", request_contact=True)
        keyboard.add(button_phone)
        await bot.send_message(message.chat.id, 'Отправьте номер', reply_markup=keyboard)
    
    # get client name
    else:
        exist = await sync_to_async(User.objects.filter)(chat_id=message.chat.id)
        if await sync_to_async(user_exists)(id=message.chat.id):
            user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
            if user.name == '':
                user.name = message.text
                await sync_to_async(user.save)()
                keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                button_routes = types.KeyboardButton(text="Маршруты")
                keyboard.add(button_routes)
                await bot.send_message(message.chat.id, 'Выберите опцию', reply_markup=keyboard)
            else:
                await bot.send_message(message.chat.id, 'Ты уебонец делай че говорят а не хуйню пиши ты гандонио ебучий мозги не еби')
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_phone = types.KeyboardButton(text="Отправить номер", request_contact=True)
            keyboard.add(button_phone)
            await bot.send_message(message.chat.id, 'Слыш ебанат регистрацию прошел быстро. Развелись тут дебилоиды. Номер свой кидай пидрилос', reply_markup=keyboard)

# Send information of a route to the client
@dp.callback_query_handler(route_cb.filter(action='order_btn'))
async def order_handler(query: CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    id = callback_data['id']
    order = await sync_to_async(Order.objects.get)(pk=id)
    time = await sync_to_async(order.update_time)()
    msg = 'Последнее обновление: {}'.format(time.strftime("%d/%m/%Y %H:%M:%S"))
    await bot.send_location(query.from_user.id, order.latitude, order.longitude)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_routes = types.KeyboardButton(text="Маршруты")
    keyboard.add(button_routes)
    await bot.send_message(query.from_user.id, msg, reply_markup=keyboard)


# For drivers
# Send location of a driver and save to database and send notification and this location to the client
@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
    lat = message.location.latitude
    lon = message.location.longitude
    order = await sync_to_async(Order.objects.get)(driver=user)
    order.latitude = lat
    order.longitude = lon
    await sync_to_async(order.save)()
    client = await sync_to_async(User.objects.get)(pk=order.client_id)
    msg = 'Местоположение обновлено \nМаршрут: {}'.format(await sync_to_async(order.get_route)())
    await bot.send_message(client.chat_id, msg)
    await bot.send_location(client.chat_id, lat, lon)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_location = types.KeyboardButton(text="Отправить локацию", request_location=True)
    keyboard.add(button_location)
    await message.answer('Местополежение отправлено', reply_markup=keyboard)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)