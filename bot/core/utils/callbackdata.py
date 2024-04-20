from aiogram.filters.callback_data import CallbackData
    
class InlineInfo(CallbackData, prefix='inline'):
    type: str
    animal: str
    IsLocated: bool
    IsContact: bool

    
