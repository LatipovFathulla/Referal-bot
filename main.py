from aiogram import Bot, Dispatcher
import asyncio
from bot import bot_router
from admin import admin_router
from database import Base, engine
bot = Bot(token="7153700160:AAEG1I8IpDQBdbQTf6w0uk4whSq6auyZtMQ")
dp = Dispatcher()
Base.metadata.create_all(bind=engine)
from database.otherservice import *

# TODO это нужно убрать после теста
try:
    add_admin_info()
    add_chanel("@refer_jabyum")
except:
    pass

async def main():
    dp.include_router(bot_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())