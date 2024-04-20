from aiogram import Bot
from aiogram.types import CallbackQuery
from core.handlers.basic import get_text
from core.keyboards.inline import get_inline_branches, get_inline_stations
from aiogram.fsm.context import FSMContext
from core.utils.statesform import ButtonsSteps, TextSteps, VoiceSteps
    
async def select_text(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer("Введи свой запрос в свободной текстовой форме:")
    await state.set_state(TextSteps.GET_TEXT)
    await call.answer()
    
async def select_voice(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer("Я принимаю запросы через обычные голосовые сообщения телеграма\nПрисылай свое!")
    await state.set_state(VoiceSteps.GET_VOICE)
    await call.answer()
    
async def select_buttons(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(ButtonsSteps.CHOOSING_BRANCH)
    context_data = await state.get_data()
    
    if (context_data.get('branch_sheet') == None):
        await state.update_data(branch_sheet = "0")

    if (call.data.endswith(">")): 
        context_data = await state.get_data()
        sheet = int(context_data.get('branch_sheet'))
        await state.update_data(branch_sheet = str(sheet+1))
    elif (call.data.endswith("<")): 
        context_data = await state.get_data()
        sheet = int(context_data.get('branch_sheet'))
        await state.update_data(branch_sheet = str(sheet-1))
    
    context_data = await state.get_data()
    sheet = int(context_data.get('branch_sheet'))
    await call.message.answer("Выбери ветку:", reply_markup=get_inline_branches(sheet))
    await call.answer()
    
async def select_station(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(ButtonsSteps.CHOOSING_STATION)
    context_data = await state.get_data()
    
    if (context_data.get('station_sheet') == None):
        await state.update_data(station_sheet = "0")

    if (call.data.endswith(">")): 
        context_data = await state.get_data()
        sheet = int(context_data.get('station_sheet'))
        await state.update_data(station_sheet = str(sheet+1))
    elif (call.data.endswith("<")): 
        context_data = await state.get_data()
        sheet = int(context_data.get('station_sheet'))
        await state.update_data(station_sheet = str(sheet-1))
    
    context_data = await state.get_data()
    sheet = int(context_data.get('station_sheet'))
    await call.message.answer("Выбери станцию:", reply_markup=get_inline_stations(sheet))
    await call.answer()
    
async def predict(call: CallbackQuery, bot: Bot, state: FSMContext):
    station = call.data.replace("station_", "")
    # здесь типо получаю предикт
    predict = "фикция"
    await call.message.answer(f"Предсказание - {predict} для {station}")
    await call.answer()
    await state.clear()
    
async def select_check(call: CallbackQuery, bot: Bot, state: FSMContext):
    context_data = await state.get_data()
    if (call.data.endswith('yes')):
        right_station = context_data.get("possible_stations")[context_data.get("check_station")]
        predict = "фикция от " + right_station # здесь типо получаю предикт
        await call.message.answer(f"Предсказание - {predict}")
        await state.clear()
    if (call.data.endswith('no')):
        check_station_new = int(context_data.get('check_station')) + 1
        await state.update_data(check_station = check_station_new)
        await state.set_state(TextSteps.GET_TEXT)
        await get_text(call.message, bot, state)
    await call.message.delete()
    await call.answer()

async def developers(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer("Данный проект, состоящий из телеграм бота, обработки естественного языка в тексте и аудио, ML модели, базы данных и API " \
                              "был создан за 24 часа на хакатоне \"Nuclear IT Hack 2024\" командой разработчиков: " \
                             "Пашинская Пелагея, Ворогушин Максим, Иванов Александр, Мичурин Артем")
    # Потом добавлю сюда же вывод общей фотографии команды
    await call.answer()
    
    
