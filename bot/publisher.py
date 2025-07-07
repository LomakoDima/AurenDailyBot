# publisher.py | MIT License | 2025 | author: DimaLab
import logging
import aiohttp
from aiogram import Bot
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.enums import ParseMode
from .config import Config

logger = logging.getLogger(__name__)


class ChannelPublisher:
    def __init__(self):
        self.bot = Bot(token=Config.BOT_TOKEN)

    async def publish_post(self, post_data: dict, parse_mode: str = None) -> bool:
        """Публикует пост с изображением или без"""
        try:
            logger.info(f"Публикация поста типа '{post_data['type']}' в канал {Config.CHANNEL_ID}")

            # Если есть изображение, публикуем с фото
            if post_data.get('image_url'):
                try:
                    image_data = post_data['image_url']
                    logger.info(f"Тип изображения: {type(image_data)}")

                    # Обрабатываем разные типы изображений
                    if isinstance(image_data, str):
                        # URL изображения
                        logger.info(f"Отправка изображения по URL: {image_data[:50]}...")
                        photo = URLInputFile(image_data)
                    elif isinstance(image_data, BufferedInputFile):
                        # Уже готовый BufferedInputFile
                        logger.info("Отправка изображения как BufferedInputFile")
                        photo = image_data
                    else:
                        logger.error(f"Неподдерживаемый тип изображения: {type(image_data)}")
                        return await self._send_text_only(post_data['text'], parse_mode)

                    message = await self.bot.send_photo(
                        chat_id=Config.CHANNEL_ID,
                        photo=photo,
                        caption=post_data['text'],
                        parse_mode=parse_mode
                    )

                    logger.info(f"Пост с изображением успешно опубликован. Message ID: {message.message_id}")
                    return True

                except Exception as img_error:
                    logger.error(f"Ошибка при отправке изображения: {img_error}")
                    logger.error(f"Детали изображения: {post_data.get('image_url')}")
                    # Отправляем только текст, если изображение не удалось
                    return await self._send_text_only(post_data['text'], parse_mode)

            # Если изображения нет, отправляем только текст
            else:
                logger.info("Изображение отсутствует, отправляем только текст")
                return await self._send_text_only(post_data['text'], parse_mode)

        except Exception as e:
            logger.error(f"Ошибка при публикации поста: {e}")
            return False

    async def _send_text_only(self, text: str, parse_mode: str = None) -> bool:
        """Отправляет только текстовое сообщение"""
        try:
            message = await self.bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )

            logger.info(f"Текстовый пост успешно опубликован. Message ID: {message.message_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при отправке текстового поста: {e}")
            return False

    async def test_connection(self) -> bool:
        """Тестирует соединение с каналом"""
        try:
            chat = await self.bot.get_chat(Config.CHANNEL_ID)
            logger.info(f"Соединение с каналом '{chat.title}' успешно")
            return True

        except Exception as e:
            logger.error(f"Ошибка соединения с каналом: {e}")
            return False

    async def close(self):
        """Закрывает соединение"""
        await self.bot.session.close()