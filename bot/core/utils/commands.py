from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Запустить бота'),
        BotCommand(command='text', description='Ввести запрос в свободной форме'),
        BotCommand(command='file', description='Ввести файл'),
        BotCommand(command='voice', description='Прислать голосовой запрос'),
        BotCommand(command='help', description='Помощь и описание'),
        BotCommand(command='cancel', description='Сбросить')
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())