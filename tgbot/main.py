import asyncio
import logging

from modules import dp, bot

if __name__ == "__main__":
    try:
        asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        logging.info("Bot was stopped by user")
