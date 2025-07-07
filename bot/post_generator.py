# post_generator.py | MIT License | 2025 | author: DimaLab
import random
import logging
from datetime import datetime
from openai import AsyncOpenAI
from .config import Config
from .image_generator import ImageGenerator

logger = logging.getLogger(__name__)


class PostGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.image_generator = ImageGenerator()
        self.prompts = {
            'motivation': self._get_motivation_prompt(),
            'fact': self._get_fact_prompt(),
            'meme': self._get_meme_prompt(),
            'devlog': self._get_devlog_prompt()
        }

    def _get_motivation_prompt(self):
        return """
        Ты - автор Telegram-канала "Таверна разработчика". 
        Создай мотивационный утренний пост о программировании на русском языке.

        Требования:
        - Начинай с "🌅 Доброе утро, Таверна разработчика!"
        - Далее мотивационное сообщение в стиле философского размышления
        - Длина: 3-5 предложений
        - Тон: дружелюбный, вдохновляющий, философский
        - С эмодзи (умеренно)
        - Закончи цитатой в кавычках и указанием автора
        - Тематика: мотивация в программировании, преодоление трудностей, рост как разработчика
        - В конце добавь хештеги: #dev #morningdev #motivation #discipline

        Формат поста должен быть как в примере:
        🌅 Доброе утро, Таверна разработчика!
        [Мотивационное сообщение]
        "[Вдохновляющая цитата]"
        — [Автор]

        [хештеги]
        """

    def _get_fact_prompt(self):
        return """
        Ты - автор Telegram-канала "Таверна разработчика".
        Создай интересный IT-факт на русском языке.

        Требования:
        - Длина: 3-5 предложений
        - Тон: познавательный, увлекательный
        - С эмодзи (умеренно)
        - Тематика: история IT, интересные факты о языках программирования, компаниях, технологиях
        - В конце добавь хештеги: #dev #morningdev #motivation #discipline

        Расскажи что-то действительно интересное, что может удивить даже опытных разработчиков.
        """

    def _get_meme_prompt(self):
        return """
        Ты - автор Telegram-канала "Таверна разработчика".
        Создай текстовый мем о программировании на русском языке.

        Требования:
        - Длина: 2-4 предложения
        - Тон: юмористический, ироничный
        - С эмодзи (умеренно)
        - Тематика: типичные ситуации программистов, баги, дедлайны, код-ревью
        - В конце добавь хештеги: #dev #morningdev #motivation #discipline

        Создай что-то, над чем засмеются все разработчики, узнав себя.
        """

    def _get_devlog_prompt(self):
        return """
        Ты - автор Telegram-канала "Таверна разработчика".
        Создай devlog пост - заметку от лица разработчика на русском языке.

        Требования:
        - Начинай с эмодзи свечи или лампы
        - Длина: 4-6 предложений
        - Тон: личный, размышляющий, философский
        - С эмодзи (умеренно)
        - Тематика: размышления о коде, архитектуре, рефакторинге, новых технологиях
        - В конце добавь хештеги: #dev #morningdev #motivation #discipline

        Напиши как разработчик, который делится своими мыслями и опытом.
        """

    async def generate_post(self, post_type: str = None) -> dict:
        """Генерирует пост заданного типа с изображением"""
        if post_type is None:
            post_type = random.choice(Config.POST_TYPES)

        if post_type not in self.prompts:
            raise ValueError(f"Неизвестный тип поста: {post_type}")

        try:
            logger.info(f"Генерация поста типа: {post_type}")

            # Генерируем текст поста
            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.prompts[post_type]},
                    {"role": "user", "content": "Создай пост"}
                ],
                max_tokens=300,
                temperature=0.8
            )

            post_content = response.choices[0].message.content.strip()

            # Генерируем изображение для определенных типов постов
            image_url = None
            if post_type in ['motivation', 'fact', 'devlog']:
                image_prompt = self._get_image_prompt_for_type(post_type)
                image_url = await self.image_generator.generate_image(image_prompt)

            logger.info(f"Пост успешно сгенерирован: {len(post_content)} символов")

            return {
                'text': post_content,
                'image_url': image_url,
                'type': post_type
            }

        except Exception as e:
            logger.error(f"Ошибка при генерации поста: {e}")
            fallback_text = self._get_fallback_post(post_type)
            return {
                'text': fallback_text,
                'image_url': None,
                'type': post_type
            }

    def _get_image_prompt_for_type(self, post_type: str) -> str:
        """Возвращает промпт для генерации изображения по типу поста"""
        if post_type == 'motivation':
            return self.image_generator.get_morning_image_prompt()
        elif post_type == 'fact':
            return self.image_generator.get_fact_image_prompt()
        elif post_type == 'devlog':
            return self.image_generator.get_devlog_image_prompt()
        else:
            return self.image_generator.get_morning_image_prompt()

    def _get_fallback_post(self, post_type: str) -> str:
        """Резервные посты на случай ошибки генерации"""
        fallback_posts = {
            'motivation': [
                """🌅 Доброе утро, Таверна разработчика!

Новый день — новые возможности для роста. Каждый баг, который мы исправляем, каждая строка кода, которую мы пишем, приближает нас к мастерству. Не бойтесь экспериментировать и учиться на своих ошибках.

"Мы не должны быть великими, чтобы начать, но мы должны начать, чтобы стать великими."
— Зиг Зиглар

#dev #morningdev #motivation #discipline""",

                """🌅 Доброе утро, Таверна разработчика!

Сегодня отличный день для написания чистого кода. Помните: лучшие разработчики не те, кто не делает ошибок, а те, кто умеет их быстро находить и исправлять. Каждый вызов — это возможность стать лучше.

"Простота — это высшая форма изощрённости."
— Леонардо да Винчи

#dev #morningdev #motivation #discipline"""
            ],
            'fact': [
                """🔍 Интересный факт: Первый компьютерный баг был найден в 1947 году адмиралом Грейс Хоппер. Это была настоящая моль, застрявшая в реле компьютера Harvard Mark II. Именно поэтому процесс исправления ошибок называется "debugging" — буквально "удаление жуков".

#dev #morningdev #motivation #discipline""",

                """🐍 Python назван в честь британского комедийного шоу "Monty Python's Flying Circus", а не в честь змеи. Гвидо ван Россум, создатель языка, был большим поклонником этой передачи и хотел, чтобы название языка было кратким и загадочным.

#dev #morningdev #motivation #discipline"""
            ],
            'devlog': [
                """💡 Сегодня потратил три часа на отладку одной функции. Оказалось, проблема была в неправильном понимании требований. Урок: иногда лучше потратить больше времени на анализ задачи, чем на написание кода. Хорошая архитектура начинается с правильного понимания проблемы.

#dev #morningdev #motivation #discipline""",

                """🕯️ Рефакторинг старого кода — это как археология. Каждый слой кода раскрывает историю принятых решений. Сегодня понял, что хорошая документация — это письмо будущему себе. Пишите код так, как будто его будет поддерживать ваш злейший враг, знающий, где вы живете.

#dev #morningdev #motivation #discipline"""
            ]
        }

        return random.choice(fallback_posts.get(post_type, fallback_posts['motivation']))

    def get_post_type_for_time(self, hour: int) -> str:
        """Определяет тип поста по времени"""
        if hour == 8:
            return 'motivation'  # Утренние мотивационные посты с изображениями
        elif hour == 14:
            return random.choice(['fact', 'meme'])
        elif hour == 19:
            return random.choice(['devlog', 'fact'])
        else:
            return random.choice(Config.POST_TYPES)