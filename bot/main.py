from aiogram import Bot, Dispatcher
from aiogram.types import Message
import asyncio
import logging 
import aiomysql

from core.utils.Confidential import DEV_TOKEN, ADMIN_ID

from aiogram.fsm.storage.redis import RedisStorage
from core.handlers.basic import command_cancel, command_file, command_help, command_predict, command_voice, get_document, get_start, get_text, get_voice, select_buttons_command, select_text_command
from core.handlers.callback import developers, get_predict, predict, select_buttons, select_check, select_station, select_text, select_voice

from aiogram.filters import Command, CommandStart, callback_data
from aiogram import F
from core.utils.commands import set_commands

from core.middlewares.dbmiddleware import DBSession
from aiogram.utils.chat_action import ChatActionMiddleware

from core.utils.statesform import DocumentSteps, TextSteps, VoiceSteps
from datetime import datetime, timedelta


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(ADMIN_ID,
                           f"Bot has been launched at {datetime.now()}")
    print('Bot has been launched')

async def stop_bot(bot: Bot):
    await bot.send_message(ADMIN_ID,
                           f"Bot has been stopped at {datetime.now()}")
    print("Bot has been stopped")

# async def create_pool():
#     return await aiomysql.create_pool(
#         host = 'localhost', 
#         port = 3306, 
#         user='root',
#         password='',
#         db='',
#         autocommit=True,
#         )

async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                        "(%(filename)s.%(funcName)s(%(lineno)d) - %(message)s")

    bot = Bot(token=DEV_TOKEN, parse_mode='HTML')
    #pool_connect = await create_pool()
    storage = RedisStorage.from_url('redis://localhost:6379/0')
    dp = Dispatcher(storage=storage) 

    # dp.update.middleware.register(DBSession(pool_connect))
    dp.message.middleware.register(ChatActionMiddleware())


    dp.message.register(get_start, Command(commands='start'))  # CommandStart()
    
    dp.message.register(select_text_command, Command(commands='text'))
    # dp.message.register(select_buttons_command, Command(commands='buttons'))

    dp.callback_query.register(select_text, F.data.contains("text"))
    # dp.callback_query.register(select_buttons, F.data.contains("buttons"))

    dp.message.register(get_text, TextSteps.GET_TEXT)
    dp.callback_query.register(select_check, TextSteps.IS_CORRECT)
    
    # dp.callback_query.register(select_buttons, F.data.contains("branch_<"))
    # dp.callback_query.register(select_buttons, F.data.contains("branch_>"))
    # dp.callback_query.register(select_station, F.data.startswith("branch_"))
    # dp.callback_query.register(select_station, F.data.contains("station_<"))
    # dp.callback_query.register(select_station, F.data.contains("station_>"))
    
    # dp.callback_query.register(predict, F.data.startswith("station_"))
    
    dp.message.register(get_document, F.document, DocumentSteps.GET_DOCUMENT)
    dp.message.register(get_voice, F.voice, VoiceSteps.GET_VOICE)
    
    dp.message.register(command_file, Command(commands='file'))
    dp.message.register(command_voice, Command(commands='voice'))
    dp.callback_query.register(select_voice, F.data.contains("voice"))
    dp.message.register(command_predict, Command(commands='predict'))
    dp.callback_query.register(get_predict, F.data.contains("predict"))
    dp.message.register(command_help, Command(commands='help'))
    dp.message.register(command_cancel, Command(commands='cancel'))
    
    dp.callback_query.register(developers, F.data.contains("developers"))    

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)


    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())