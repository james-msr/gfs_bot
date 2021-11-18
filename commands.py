from config import *
from utils import *
from keyboads import *

from aiogram.types.message import Message
from asgiref.sync import sync_to_async

from bot.models import User, Order


# Command handlers
# Ask phone number after command start
@dp.message_handler(commands=['start'])
async def phone(message: Message):
    keyboard = start_keyboard()
    await bot.send_message(message.chat.id, 'Отправьте номер телефона', reply_markup=keyboard)


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
        keyboard = sendnum_keyboard()
        await bot.send_message(message.chat.id, 'Отправьте номер', reply_markup=keyboard)


@dp.message_handler(commands=['authorize'])
async def authorize(message: Message):
    if await sync_to_async(user_exists)(message.chat.id):
        if await sync_to_async(is_client)(message.chat.id):
            await bot.send_message(message.chat.id, 'Ты еблан? Ты уже авторизован долбаеб')
        else:
            await bot.send_message(message.chat.id, 'Бля эти команды нахуй не нажимай. Не для твоих мазолевых рук')
    else:
        keyboard = sendnum_keyboard()
        await bot.send_message(message.chat.id, 'Отправьте номер', reply_markup=keyboard)


@dp.message_handler(commands=['active'])
async def active_routes(message: Message):
    # if await sync_to_async(user_exists)(message.chat.id):
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
    # else:
    #     await bot.send_message(message.chat.id, "Сначала ебись, потом кончай, а не наоборот. Сначала регайся и авторизуйся потом уже спрашивай свои ебаные маршруты жалаб")


@dp.message_handler(commands=['finished'])
async def finished_routes(message: Message):
    user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
    orders = await sync_to_async(list)(Order.objects.filter(client=user, finished=True))
    msg = ''
    for order in orders[:5]:
        name = await sync_to_async(order.get_route)()
        time = order.finish_time
        msg += 'Маршрут:\n{}\nВремя окончания:\n{}\n\n\n'.format(name, time.strftime("%d/%m/%Y %H:%M:%S"))
    await bot.send_message(message.chat.id, msg)