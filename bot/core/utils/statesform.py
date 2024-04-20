from aiogram.fsm.state import StatesGroup, State

    
class TextSteps(StatesGroup):
    GET_TEXT = State()
    IS_CORRECT = State()


class ButtonsSteps(StatesGroup):
    CHOOSING_BRANCH = State()
    CHOOSING_STATION = State()

class DocumentSteps(StatesGroup):
    GET_DOCUMENT = State()
    
class VoiceSteps(StatesGroup):
    GET_VOICE = State()
    


