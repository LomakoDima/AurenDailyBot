# debug_images.py - Подробная отладка публикации изображений
import asyncio
import logging
from bot import ImageGenerator, PostGenerator, ChannelPublisher, Config

# Настраиваем подробное логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_image_generation():
    """Тестирует только генерацию изображений"""
    print("🧪 Тестирование генерации изображений...")

    generator = ImageGenerator()

    # Тестируем простой промпт
    test_prompt = "A simple computer workspace with code on screen"
    print(f"\n📝 Тестовый промпт: {test_prompt}")

    try:
        result = await generator.generate_image(test_prompt)

        if result is None:
            print("❌ Результат: None - изображение не сгенерировано")
            return False
        else:
            print(f"✅ Результат: {type(result)}")
            if isinstance(result, str):
                print(f"📄 URL: {result[:100]}...")
                return result
            else:
                print(f"📄 BufferedInputFile: {result.filename if hasattr(result, 'filename') else 'no filename'}")
                return result

    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        logger.exception("Подробная ошибка:")
        return False


async def test_post_generation():
    """Тестирует полную генерацию поста с изображением"""
    print("\n📄 Тестирование генерации поста...")

    generator = PostGenerator()

    try:
        post_data = await generator.generate_post('motivation')

        print(f"✅ Пост сгенерирован:")
        print(f"  Тип: {post_data['type']}")
        print(f"  Текст: {post_data['text'][:100]}...")
        print(f"  Изображение: {type(post_data['image_url']) if post_data['image_url'] else 'None'}")

        if post_data['image_url']:
            if isinstance(post_data['image_url'], str):
                print(f"  URL: {post_data['image_url'][:100]}...")
            else:
                print(f"  BufferedInputFile: {post_data['image_url']}")

        return post_data

    except Exception as e:
        print(f"❌ Ошибка генерации поста: {e}")
        logger.exception("Подробная ошибка:")
        return None


async def test_telegram_connection():
    """Тестирует подключение к Telegram"""
    print("\n🔗 Тестирование подключения к Telegram...")

    publisher = ChannelPublisher()

    try:
        connection_ok = await publisher.test_connection()
        if connection_ok:
            print("✅ Подключение к каналу успешно")
        else:
            print("❌ Не удалось подключиться к каналу")

        await publisher.close()
        return connection_ok

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        logger.exception("Подробная ошибка:")
        return False


async def test_image_publishing():
    """Тестирует публикацию изображения"""
    print("\n📸 Тестирование публикации изображения...")

    publisher = ChannelPublisher()

    # Создаем тестовый пост с изображением
    test_post = {
        'text': '🧪 Тестовый пост с изображением от бота\n\n#test #debug',
        'image_url': 'https://picsum.photos/1024/1024?random=1',  # Тестовое изображение
        'type': 'test'
    }

    try:
        success = await publisher.publish_post(test_post)
        if success:
            print("✅ Тестовое изображение успешно опубликовано")
        else:
            print("❌ Не удалось опубликовать тестовое изображение")

        await publisher.close()
        return success

    except Exception as e:
        print(f"❌ Ошибка публикации: {e}")
        logger.exception("Подробная ошибка:")
        await publisher.close()
        return False


async def test_full_workflow():
    """Тестирует полный workflow: генерация + публикация"""
    print("\n🔄 Тестирование полного workflow...")

    generator = PostGenerator()
    publisher = ChannelPublisher()

    try:
        # Генерируем пост
        post_data = await generator.generate_post('motivation')

        if not post_data:
            print("❌ Не удалось сгенерировать пост")
            return False

        print(f"✅ Пост сгенерирован с изображением: {post_data['image_url'] is not None}")

        # Публикуем пост
        success = await publisher.publish_post(post_data)

        if success:
            print("✅ Пост с изображением успешно опубликован!")
        else:
            print("❌ Не удалось опубликовать пост")

        await publisher.close()
        return success

    except Exception as e:
        print(f"❌ Ошибка в workflow: {e}")
        logger.exception("Подробная ошибка:")
        await publisher.close()
        return False


async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск комплексной отладки...")

    # Проверяем конфигурацию
    try:
        Config.validate()
        print("✅ Конфигурация корректна")
        print(f"  IMAGE_MODEL: {Config.IMAGE_MODEL}")
        print(f"  IMAGE_SIZE: {Config.IMAGE_SIZE}")
        print(f"  IMAGE_QUALITY: {Config.IMAGE_QUALITY}")
        print(f"  CHANNEL_ID: {Config.CHANNEL_ID}")
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return

    # Тестируем по шагам
    results = []

    # 1. Генерация изображения
    image_result = await test_image_generation()
    results.append(("Генерация изображения", image_result is not False))

    # 2. Генерация поста
    post_result = await test_post_generation()
    results.append(("Генерация поста", post_result is not None))

    # 3. Подключение к Telegram
    connection_result = await test_telegram_connection()
    results.append(("Подключение к Telegram", connection_result))

    # 4. Публикация тестового изображения
    if connection_result:
        image_pub_result = await test_image_publishing()
        results.append(("Публикация тестового изображения", image_pub_result))

    # 5. Полный workflow
    if all(r[1] for r in results):
        workflow_result = await test_full_workflow()
        results.append(("Полный workflow", workflow_result))

    # Выводим итоги
    print("\n📊 Результаты тестирования:")
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}")

    if all(r[1] for r in results):
        print("\n🎉 Все тесты пройдены успешно!")
    else:
        print("\n⚠️  Есть проблемы, требующие исправления")


if __name__ == "__main__":
    asyncio.run(main())