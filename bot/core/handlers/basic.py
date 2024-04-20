from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import json
from core.keyboards.inline import get_inline_branches, get_inline_check, get_inline_developers, get_inline_start
from core.utils.dbconnect import Request
from core.utils.statesform import ButtonsSteps, DocumentSteps, TextSteps, VoiceSteps


async def get_start(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Привет!\nЯ - бот для хакатона Nuclear Hack. \nЯ создан, чтобы помогать людям узнавать " \
                         "загруженность станций Московского метро в любой день и время!\n" \
                         "Отправь команду \"\\help\", чтобы узнать подробнее о доступных командах и разработчиках", reply_markup=get_inline_start() )


async def get_text(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(text = message.text)
    context_data = await state.get_data()
    if (context_data.get('possible_stations') == None):
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
            # state.set_data({})
        else:
            await message.answer(f"Выбранная станция {get_possible_stations[check_station]} - Верно?", reply_markup=get_inline_check())

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
    file_type = message.document.file_name.split(".")[1]
    
    if (file_type == "csv" or file_type == "xslx"):
        await message.answer(f'Отлично, ты отправил докумет! Я добавлю его в данные.')
        await bot.download_file(file.file_path, 'doc' + str(file.file_id) + "." + file_type)
    else:
        await message.answer(f"Бот принимает данные для обновления только в форматах .csv и .xslx")
        
async def command_voice(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Я принимаю запросы через обычные голосовые сообщения телеграма\nПрисылай свое!")
    await state.set_state(VoiceSteps.GET_VOICE)

async def get_voice(message: Message, bot: Bot):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    print(*file)
    await bot.download_file(file_path, "voices/" + str(file_id) +".oga")
    await message.answer("Я принял твой голосовой запрос! Сейчас обработаю его.")
    
async def command_cancel(message: Message, bot: Bot, state: FSMContext):
    await state.clear()

async def command_help(message: Message, bot: Bot):
    await message.answer("Чтобы начать работу с ботом и получить приветственное сообщение отправь команду \"\\start\"\n" \
                        "Чтобы ввести запрос в свободной форме отправь команду \"\\text\"\n" \
                        "Чтобы отправить новые данные для ML модели боту отправь команду \"\\file\"\n" \
                       "Чтобы сделать запрос голосовым сообщением отправь команду \"\\voice\"\n" \
                       "Чтобы сбросить текущий запрос к ML модели отправь команду \"\\voice\"\n", reply_markup=get_inline_developers())



