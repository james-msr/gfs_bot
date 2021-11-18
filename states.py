from aiogram.dispatcher.filters.state import State, StatesGroup



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


class AdminStates(StatesGroup):
    wait_for_id = State('chat_id', 'admin')
    wait_fot_text = State('text', 'admin')