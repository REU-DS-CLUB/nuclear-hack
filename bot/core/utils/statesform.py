from aiogram.fsm.state import StatesGroup, State

class StepsForm(StatesGroup):
    GET_NAME = State()
    GET_LAST_NAME = State()
    GET_AGE = State()
    
class TextSteps(StatesGroup):
    GET_TEXT = State()
    IS_CORRECT = State()


class ButtonsSteps(StatesGroup):
    CHOOSING_BRANCH = State()
    CHOOSING_STATION = State()


