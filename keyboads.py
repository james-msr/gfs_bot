from aiogram import types
from aiogram.utils.callback_data import CallbackData


route_cb = CallbackData('route', 'action', 'id')

order_cb = CallbackData('order', 'action')

def start_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер", request_contact=True)
    keyboard.add(button_phone)
    return keyboard

def sendnum_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер", request_contact=True)
    keyboard.add(button_phone)
    return keyboard

def routes_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_active_routes = types.KeyboardButton(text="Активные маршруты")
    keyboard.add(button_active_routes)
    button_finished_routes = types.KeyboardButton(text="Оконченные маршруты")
    keyboard.add(button_finished_routes)
    button_new_route = types.KeyboardButton(text="Отправить заявку на перевозку")
    keyboard.add(button_new_route)
    return keyboard

def location_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_location = types.KeyboardButton(text="Отправить локацию", request_location=True)
    keyboard.add(button_location)
    return keyboard

def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_location = types.KeyboardButton(text="Отменить заявку", request_location=True)
    keyboard.add(button_location)
    return keyboard
