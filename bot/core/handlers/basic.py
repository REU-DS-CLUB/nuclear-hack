from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import json
from core.keyboards.inline import get_inline_branches, get_inline_check, get_inline_start
from core.utils.dbconnect import Request
from core.utils.statesform import ButtonsSteps, TextSteps


async def get_inline(message: Message, bot: Bot):
    await message.answer('Hello, its inline buttons', reply_markup=get_inline_keyboard())

async def get_start(message: Message, bot: Bot, state: FSMContext):
    # await request.create_feedback(message.from_user.id)

    # await message.answer(f'Сообщение #{counter}')
    # await bot.send_message(message.from_user.id, f"{message.from_user.first_name}, а ты знал, что <b>Это send_message</b> ")
    await message.answer("Привет!\nЯ - бот для хакатона Nuclear Hack. \nЯ создан, чтобы помогать людям узнавать загруженность станций" \
                         "\nЧтобы ввести запрос в свободной форме отправь команду \"\\text\"" \
                         "\nЧтобы воспользоваться кнопками для выбора станции отправь команду \"\\buttons\" ", reply_markup=get_inline_start() )
    # await message.reply(f"Это message.reply")
    # await bot.send_message(message.from_user.id,
     #                      f"Твой id: {message.from_user.id}", reply_markup=get_reply_keyboard())

async def get_text(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(text = message.text)
    # Здесь типо парсинг и выделение станции из запроса, но пока просто текст
    await message.answer(f"Выбранная станция {message.text} - Верно?", reply_markup=get_inline_check())
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
    

async def get_document(message: Message, bot: Bot):
    file = await bot.get_file(message.document.file_id)
    file_type = message.document.file_name.split(".")[1]
    
    if (file_type == "csv" or file_type == "xslx"):
        await message.answer(f'Отлично, ты отправил докумет! Я добавлю его в данные.')
        await bot.download_file(file.file_path, 'doc' + str(file.file_id) + "." + file_type)
    else:
        await message.answer(f"Бот принимает данные для обновления только в форматах .csv и .xslx")
        
async def get_voice(message: Message, bot: Bot):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    print(*file)
    await bot.download_file(file_path, "voice" + str(file_id) +".oga")
    await message.answer("Я принял твой голосовой запрос! Сейчас обработаю его.")

    



