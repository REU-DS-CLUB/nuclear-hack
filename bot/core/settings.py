from environs import Env
from dataclasses import dataclass
# Что это за нахуй вообще????????????????????????????????????????????

@dataclass
class Bots:
    bot_token: str
    admin_id: int

@dataclass
class Settings:
    bots: Bots

def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(bots=Bots(bot_token=env.str("DEV_TOKEN"), admin_id=env.int("ADMIN_ID")))

Setting = get_settings(r'D:\source\repos\nuclear-hack\bot\Confidential')