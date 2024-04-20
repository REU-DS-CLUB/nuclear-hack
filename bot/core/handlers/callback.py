from aiogram import Bot
from aiogram.types import CallbackQuery
from core.keyboards.inline import get_inline_branches, get_inline_stations
from aiogram.fsm.context import FSMContext
from core.utils.statesform import ButtonsSteps, TextSteps
    
async def select_text(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer("Введи свой запрос в свободной текстовой форме:")
    await state.set_state(TextSteps.GET_TEXT)
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
    if (call.data.endswith('yes')):
        # здесь типо получаю предикт
        predict = "фикция"
        await call.message.answer(f"Предсказание - {predict}")
        await state.clear()
    if (call.data.endswith('no')):
        await call.message.answer("Введи свой запрос в свободной текстовой форме:")
        await state.set_state(TextSteps.GET_TEXT)
    await call.answer()

    
    
