from os import fsdecode
from aiogram import Dispatcher, Bot, executor, types
from aiogram.dispatcher.filters import state
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import Message
from asgiref.sync import sync_to_async
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from commands import *
from config import *
from keyboads import *

from bot.models import User, Order


class OrderStates(StatesGroup):
    wait_for_route_from = State('route_from', 'client')
    wait_for_route_to = State('route_to', 'client')
    wait_for_cargo_name = State('cargo_name', 'client')
    wait_for_cargo_weight = State('cargo_weight', 'client')
    wait_for_date = State('date', 'client')


class ClientStates(StatesGroup):
    wait_for_name = State('client_name', 'client')
    wait_for_option = State('option', 'client')
    wait_for_route = State('route', 'client')


@dp.message_handler(content_types=['text'], state=OrderStates.all_states)
async def order_handler(message: types.Message, state: FSMContext):
    print(await state.get_state())
    keyboard = cancel_keyboard()
    if message.text == 'Отменить заявку':
        keyboard = routes_keyboard()
        await bot.send_message(message.chat.id, 'Заявка отменена', reply_markup=keyboard)
        await ClientStates.wait_for_option.set()
    elif await state.get_state() == OrderStates.wait_for_route_from.state:
        await state.update_data(_from=message.text)
        await bot.send_message(message.chat.id, 'Куда', reply_markup=keyboard)
        await OrderStates.next()
    elif await state.get_state() == OrderStates.wait_for_route_to.state:
        await state.update_data(_to=message.text)
        await bot.send_message(message.chat.id, 'Отправьте наименование груза', reply_markup=keyboard)
        await OrderStates.next()
    elif await state.get_state() == OrderStates.wait_for_cargo_name.state:
        await state.update_data(cargo=message.text)
        await bot.send_message(message.chat.id, 'Укажите вес груза', reply_markup=keyboard)
        await OrderStates.next()
    elif await state.get_state() == OrderStates.wait_for_cargo_weight.state:
        await state.update_data(weight=message.text)
        await bot.send_message(message.chat.id, 'Введите дату перевозки в формате гггг-мм-дд', reply_markup=keyboard)
        await OrderStates.next()
    elif await state.get_state() == OrderStates.wait_for_date.state:
        if date_valid(message.text):
            await state.update_data(date=message.text)
            data = await state.get_data()
            order = await sync_to_async(Order.objects.create)(**data)
            client = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
            order.client = client
            order.phone_num = client.phone_num
            await sync_to_async(order.save)()
            await state.finish()
            keyboard = routes_keyboard()
            await bot.send_message(message.chat.id, 'Ваша заявка принята', reply_markup=keyboard)
            await ClientStates.wait_for_option.set()
        else:
            await bot.send_message(message.chat.id, 'Введите правильную форму даты', reply_markup=keyboard)


@dp.message_handler(content_types=['text'], state=ClientStates.wait_for_option)
async def select_option(message: types.Message, state: FSMContext):

    if message.text == 'Активные маршруты':
        user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
        orders = await sync_to_async(list)(Order.objects.filter(client=user, finished=False))
        if orders != []:
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            for order in orders:
                order_name = await sync_to_async(order.get_route)()
                button = types.InlineKeyboardButton(order_name, callback_data=route_cb.new(action='order_btn', id=order.id))
                keyboard.add(button)
            await bot.send_message(message.chat.id, "Маршруты", reply_markup=keyboard)
            await ClientStates.next()
        else:
            await bot.send_message(message.chat.id, "Список ваших активных маршрутов пуст")
            await state.finish()
    
    elif message.text == 'Оконченные маршруты':
        user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
        orders = await sync_to_async(list)(Order.objects.filter(client=user, finished=True))
        msg = 'Последние 5 маршрутов:\n\n'
        for order in orders[:5]:
            name = await sync_to_async(order.get_route)()
            time = order.finish_time
            msg += 'Маршрут:\n{}\nВремя окончания:\n{}\n\n\n'.format(name, time.strftime("%d/%m/%Y %H:%M:%S"))
        await bot.send_message(message.chat.id, msg)
        await state.finish()

    elif message.text == 'Отправить заявку на перевозку':
        await bot.send_message(message.chat.id, 'Укажите маршрут, откуда')
        await OrderStates.wait_for_route_from.set()
    
    else:
        keyboard = routes_keyboard()
        await bot.send_message(message.chat.id, 'Выберите один вариант из предложенных', reply_markup=keyboard)


# Get user by phone number and match to client or driver if user is already registerd
# Save phone number of a new created user if user is registering
@dp.message_handler(content_types=['contact'])
async def contact(message: Message):
    if message.contact is not None:
        # get phone number
        keyboard2 = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, 'Вы успешно отправили свой номер', reply_markup=keyboard2)
        if str(message.contact.phone_number)[0] == '+':
            phonenumber= str(message.contact.phone_number)[1:]
        else:
            phonenumber= str(message.contact.phone_number)

        # If user exist in db
        if await sync_to_async(user_exists)(phone=phonenumber):
            user = await sync_to_async(User.objects.get)(phone_num=phonenumber)
            user.chat_id = message.chat.id
            await sync_to_async(user.save)()
            # for clients
            if user.user_type == 'client':
                keyboard = routes_keyboard()
                print(keyboard.values)
                
                await client_commands()
                await ClientStates.wait_for_option.set()
            # for drivers
            else:
                keyboard = location_keyboard()
            await bot.send_message(message.chat.id, 'Выберите опцию', reply_markup=keyboard)
        
        # If user is not is db
        else:
            user = await sync_to_async(User.objects.create)()
            user.phone_num = phonenumber
            user.user_type = 'client'
            user.chat_id = message.chat.id
            await sync_to_async(user.save)()
            await bot.send_message(message.chat.id, 'Введите свое имя')
            await ClientStates.wait_for_name.set()


# For clients
# Handle text messages of the client
@dp.message_handler(content_types=['text'], state=ClientStates.wait_for_name)
async def get_name(message: Message, state: FSMContext):
    user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
    user.name = message.text
    await sync_to_async(user.save)()
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_routes = types.KeyboardButton(text="Маршруты")
    keyboard.add(button_routes)
    await client_commands()
    await bot.send_message(message.chat.id, 'Выберите опцию', reply_markup=keyboard)
    await ClientStates.next()


@dp.message_handler(content_types=['text'])
async def non_state(message: types.Message):
    if await sync_to_async(user_exists)(id=message.chat.id):
        keyboard = routes_keyboard()
        await bot.send_message(message.chat.id, 'Пожалуйста, выберите одну из опций', reply_markup=keyboard)
        await ClientStates.wait_for_option.set()
    else:
        keyboard = sendnum_keyboard()
        await bot.send_message(message.chat.id, 'Вы не зарегистрированы в нашей базе, пожалуйста, отправьте свой номер', reply_markup=keyboard)


# Send information of a route to the client
@dp.callback_query_handler(route_cb.filter(action='order_btn'), state=ClientStates.wait_for_route)
async def order_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    id = callback_data['id']
    order = await sync_to_async(Order.objects.get)(pk=id)
    time = order.last_update
    msg = None
    try:
        await bot.send_location(query.from_user.id, order.latitude, order.longitude)
        msg = 'Последнее обновление: {}'.format(time.strftime("%d/%m/%Y %H:%M:%S"))
    except:
        msg = 'Водитель находится в ожидании погрузки'
    finally:
        keyboard = routes_keyboard()
        await bot.send_message(query.from_user.id, msg, reply_markup=keyboard)
        await state.finish()


# For drivers
# Send location of a driver and save to database and send notification and this location to the client
@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    user = await sync_to_async(User.objects.get)(chat_id=message.chat.id)
    lat = message.location.latitude
    lon = message.location.longitude
    print(message.location)
    order = await sync_to_async(Order.objects.get)(driver=user)
    order.latitude = lat
    order.longitude = lon
    await sync_to_async(order.update_time)()
    await sync_to_async(order.save)()
    client = await sync_to_async(User.objects.get)(pk=order.client_id)
    msg = 'Местоположение обновлено \nМаршрут: {}'.format(await sync_to_async(order.get_route)())
    await bot.send_message(client.chat_id, msg)
    await bot.send_location(client.chat_id, lat, lon)
    keyboard = location_keyboard()
    await message.answer('Местополежение отправлено', reply_markup=keyboard)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)