from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_user_search = State()
    waiting_for_admin_id = State()
    waiting_for_broadcast_message = State()
    waiting_for_remove_admin_id = State()
