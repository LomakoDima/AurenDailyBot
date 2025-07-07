# main.py | MIT License | 2025 | author: DimaLab
import asyncio
import logging
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from bot import Config, PostGenerator, ChannelPublisher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramChannelBot:
    def __init__(self):
        self.generator = PostGenerator()
        self.publisher = ChannelPublisher()
        self.scheduler = AsyncIOScheduler()
        self.timezone = pytz.timezone(Config.TIMEZONE)

    async def generate_and_publish_post(self):
        """Генерирует и публикует пост"""
        try:
            current_hour = datetime.now(self.timezone).hour
            post_type = self.generator.get_post_type_for_time(current_hour)

            logger.info(f"Начинаем генерацию поста типа '{post_type}' в {current_hour}:00")

            # Генерируем пост (теперь возвращается словарь с текстом и изображением)
            post_data = await self.generator.generate_post(post_type)

            # Публикуем пост
            success = await self.publisher.publish_post(post_data)

            if success:
                logger.info(f"Пост успешно опубликован: {post_data['text'][:50]}...")
            else:
                logger.error("Не удалось опубликовать пост")

        except Exception as e:
            logger.error(f"Ошибка при генерации и публикации поста: {e}")

    async def test_bot_setup(self):
        """Тестирует настройку бота"""
        logger.info("Тестирование настройки бота...")

        if await self.publisher.test_connection():
            logger.info("✓ Соединение с каналом успешно")
        else:
            logger.error("✗ Не удалось подключиться к каналу")
            return False

        try:
            test_post = await self.generator.generate_post('motivation')
            logger.info(f"✓ Генерация поста работает: {test_post['text'][:30]}...")
        except Exception as e:
            logger.error(f"✗ Ошибка генерации поста: {e}")
            return False

        return True

    async def publish_test_post(self):
        """Публикует тестовый пост"""
        logger.info("Публикация тестового поста...")

        test_post_data = {
            'text': "🧪 Тестовый пост от бота канала 'Таверна разработчика'. Автоматическая публикация работает!\n\n#dev #test",
            'image_url': None,
            'type': 'test'
        }

        success = await self.publisher.publish_post(test_post_data)
        if success:
            logger.info("✓ Тестовый пост успешно опубликован")
        else:
            logger.error("✗ Не удалось опубликовать тестовый пост")

        return success

    def setup_scheduler(self):
        """Настраивает планировщик задач"""
        logger.info("Настройка планировщика...")

        for hour, minute in Config.POST_SCHEDULE:
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                second=0,
                timezone=self.timezone
            )

            self.scheduler.add_job(
                self.generate_and_publish_post,
                trigger=trigger,
                id=f'post_job_{hour}',
                name=f'Публикация поста в {hour}:00',
                misfire_grace_time=300
            )

            logger.info(f"Добавлена задача: публикация в {hour}:00")

    async def start(self):
        """Запускает бота"""
        logger.info("Запуск бота...")

        try:
            Config.validate()
            logger.info("✓ Конфигурация валидна")
        except ValueError as e:
            logger.error(f"✗ Ошибка конфигурации: {e}")
            return

        if not await self.test_bot_setup():
            logger.error("✗ Тестирование не пройдено, остановка")
            return

        self.setup_scheduler()

        self.scheduler.start()
        logger.info("✓ Планировщик запущен")

        jobs = self.scheduler.get_jobs()
        logger.info(f"Активные задачи: {len(jobs)}")
        for job in jobs:
            logger.info(f"  - {job.name} (следующий запуск: {job.next_run_time})")

        logger.info("🎉 Бот успешно запущен и готов к работе!")

        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки...")
        finally:
            await self.stop()

    async def stop(self):
        """Останавливает бота"""
        logger.info("Остановка бота...")

        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✓ Планировщик остановлен")

        await self.publisher.close()
        logger.info("✓ Соединения закрыты")

        logger.info("🛑 Бот остановлен")


async def main():
    bot = TelegramChannelBot()

    # Для тестирования - раскомментируйте нужную строку:
    # await bot.publish_test_post()  # Опубликовать тестовый пост
    # await bot.generate_and_publish_post()  # Сгенерировать и опубликовать пост сейчас

    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())