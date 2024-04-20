import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, keyboard_button
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_start():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Ввести запрос в свободной форме', callback_data="text" )
    # keyboard_builder.button(text='Воспользоваться кнопками для выбора станции', callback_data="buttons")
    
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def get_inline_check():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Да', callback_data="check_yes" )
    keyboard_builder.button(text='Нет', callback_data="check_no")
    
    keyboard_builder.adjust(1, 1)
    return keyboard_builder.as_markup()




def get_inline_branches(sheet: int):
    data = ["green", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow"]
    some_json = json.dumps(data)
    some_data = json.loads(some_json)
    max_i = len(some_data)    

    keyboard_builder = InlineKeyboardBuilder()
    for i in range(10):
        if (i + int(sheet)*10 < max_i):
            keyboard_builder.button(text=some_data[i+sheet*10], callback_data="branch_"+some_data[i+sheet*10] )
        else:
            break

    keyboard_builder.button(text="<", callback_data="branch_<")
    keyboard_builder.button(text=">", callback_data="branch_>")
    keyboard_builder.adjust(4, 4, 4)
    return keyboard_builder.as_markup()

def get_inline_stations(sheet: int):
    data = ["station1", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2", "station2" ]
    some_json = json.dumps(data)
    some_data = json.loads(some_json)
    max_i = len(some_data)    

    keyboard_builder = InlineKeyboardBuilder()
    for i in range(10):
        if (i + int(sheet)*10 < max_i):
            keyboard_builder.button(text=some_data[i+sheet*10], callback_data="station_"+some_data[i+sheet*10] )
        else:
            break

    keyboard_builder.button(text="<", callback_data="station_<")
    keyboard_builder.button(text=">", callback_data="station_>")
    keyboard_builder.adjust(4, 4, 4)
    return keyboard_builder.as_markup()

# def get_inline_animal():
#     keyboard_builder = InlineKeyboardBuilder()
#     keyboard_builder.button(text='Кот', callback_data=InlineInfo(type='', IsLocated=False, IsContact=False, animal='cat'))
#     keyboard_builder.button(text='Собака', callback_data=InlineInfo(type='', IsLocated=False, IsContact=False, animal='dog'))
    
#     keyboard_builder.adjust(2)
#     return keyboard_builder.as_markup()

# def get_inline_geo_contact():
#     keyboard_builder = InlineKeyboardBuilder()
#     keyboard_builder.button(text='Отправить геолокацию', callback_data=InlineInfo(IsLocated=True, IsContact=False, type='', animal=''), request_location = True)
#     keyboard_builder.button(text='Отправить свой контакт', callback_data=InlineInfo(IsLocated=False, IsContact=True, type='', animal=''), request_contact = True)
    
#     keyboard_builder.adjust(1, 1)
#     return keyboard_builder.as_markup()