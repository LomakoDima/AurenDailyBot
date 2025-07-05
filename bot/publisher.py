import logging
from aiogram import Bot
from aiogram.enums import ParseMode
from .config import Config

logger = logging.getLogger(__name__)


class ChannelPublisher:
    def __init__(self):
        self.bot = Bot(token=Config.BOT_TOKEN)

    async def publish_post(self, content: str, parse_mode: str = None) -> bool:
        try:
            logger.info(f"Публикация поста в канал {Config.CHANNEL_ID}")

            message = await self.bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=content,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )

            logger.info(f"Пост успешно опубликован. Message ID: {message.message_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при публикации поста: {e}")
            return False

    async def test_connection(self) -> bool:
        try:
            chat = await self.bot.get_chat(Config.CHANNEL_ID)
            logger.info(f"Соединение с каналом '{chat.title}' успешно")
            return True

        except Exception as e:
            logger.error(f"Ошибка соединения с каналом: {e}")
            return False

    async def close(self):
        await self.bot.session.close()
