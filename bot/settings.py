import os
import asyncio
import logging
import aiogram
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('market')


storage = RedisStorage2(db=5, host='redis')
loop = asyncio.get_event_loop()
bot = aiogram.Bot(token=os.environ.get('BOT_TOKEN'), parse_mode='html', loop=loop)
dp = Dispatcher(bot, storage=storage)

SUPPORT = os.environ.get('SUPPORT')
BOT_NAME = loop.run_until_complete(bot.get_me()).username

API_HOST = 'http://trading_api:8080'
