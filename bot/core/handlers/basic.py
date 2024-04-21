import os
from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
import json
from core.utils.features import get_day_plot
from core.keyboards.inline import get_inline_branches, get_inline_check, get_inline_developers, get_inline_start
from core.utils.dbconnect import Request
from core.utils.statesform import ButtonsSteps, DocumentSteps, PredictSteps, TextSteps, VoiceSteps
import core.Promts.promt as pt
import core.utils.request as rq



async def get_start(message: Message, bot: Bot, state: FSMContext):
    await message.answer(pt.command_start, reply_markup=get_inline_start() )


async def get_text(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(text = message.text)
    context_data = await state.get_data()
    if (context_data.get('possible_stations') == None):
        await message.answer(f"Отправляю запрос на массив вариантов по тексту: {context_data.get('text')}")
        get_possible_stations = ['1', '2', '3'] # Здесь обращаюсь к предварительной АПИ функции Темы и получаю массив из 3 версий
        await state.update_data(possible_stations = get_possible_stations)
        await state.update_data(check_station = 0)
        await message.answer(f"Выбранная станция {get_possible_stations[0]} - Верно?", reply_markup=get_inline_check())
    else:
        check_station = int(context_data.get('check_station'))
        get_possible_stations = context_data.get("possible_stations")
        if (check_station > 2):
            await message.answer(f"Я не смог корректно обработать твой запрос. Пожалуйста, попробуй еще раз позже")
            await state.clear()
        else:
            await message.answer(f"Выбранная станция {get_possible_stations[str(check_station)]} - Верно?", reply_markup=get_inline_check())

    await state.set_state(TextSteps.IS_CORRECT)
    
async def select_buttons_command(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(ButtonsSteps.CHOOSING_BRANCH)
    context_data = await state.get_data()
    
    if (context_data.get('branch_sheet') == None):
        await state.update_data(branch_sheet = "0")
    
    context_data = await state.get_data()
    sheet = int(context_data.get('branch_sheet'))
    await message.answer("Выбери ветку:", reply_markup=get_inline_branches(sheet))
    
async def select_text_command(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Введи свой запрос в свободной текстовой форме:")
    await state.set_state(TextSteps.GET_TEXT)
    
async def command_file(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Я принимаю новые данные в файлах с форматами .csv и .xlsx\nПрисылай свой файл!")
    await state.set_state(DocumentSteps.GET_DOCUMENT)

async def get_document(message: Message, bot: Bot):
    file = await bot.get_file(message.document.file_id)
    file_name, file_type = message.document.file_name.split(".")
    
    if (file_type == "csv" or file_type == "xlsx"):
        await message.answer(f'Отлично, ты отправил документ! Я добавлю его в данные.')
        path = 'documents/' + str(file.file_id) + "." + file_type
        await bot.download_file(file.file_path, path)
        response = await rq.document(name=file_name, path=path)
        if (response.status_code == 200):
            await message.answer('Успешно добавлено')  
        else:
            await message.answer('Произошла ошибка, попробуйте позже')
        if (os.path.exists(path=path)):
                os.remove(path=path)
    else:
        await message.answer(f"Бот принимает данные для обновления только в форматах .csv и .xslx")
        
async def command_voice(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Я принимаю запросы через обычные голосовые сообщения телеграма\nПрисылай свое!")
    await state.set_state(VoiceSteps.GET_VOICE)

async def get_voice(message: Message, bot: Bot, state: FSMContext):  
    context_data = await state.get_data()
    
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    path = "voices/" + str(file_id) +".oga"
    await bot.download_file(file_path, path)
    
    response = await rq.voice(path)
    if (response.status_code == 200): # type(response) != int and 
        await message.answer(f'{response.content.decode("UTF-8")}')
        print(response.content)
        
        get_possible_stations = response.content #json
        
        await state.update_data(possible_stations = get_possible_stations)
        await state.update_data(check_station = 0)
        await message.answer(f"Выбранная станция {get_possible_stations['0']} - Верно?", reply_markup=get_inline_check())
        await state.set_state(TextSteps.IS_CORRECT)
    else:
        await message.answer('Произошла ошибка, попробуйте позже')
        await state.clear()
    if (os.path.exists(path=path)):
                os.remove(path=path)
    
async def command_predict(message: Message, bot: Bot, state: FSMContext):
    await message.answer("На какой станции нужно предсказать пассажиропоток на завтра?")
    await state.set_state(PredictSteps.GET_STATION)
    
async def get_station_for_predict(message: Message, bot: Bot, state: FSMContext):
    predict = 0 # API REQUEST
    await message.answer(f"Прогнозируемый пассажиропоток: {predict}")
    
    grath = FSInputFile(get_day_plot())
    await bot.send_photo(message.chat.id, grath, caption="Распределение пассажиропотока по часам")
    await state.clear()
        
    
async def command_cancel(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await message.answer("Текущий запрос завершен досрочно")

async def command_help(message: Message, bot: Bot):
    await message.answer(pt.command_help, reply_markup=get_inline_developers())
    




