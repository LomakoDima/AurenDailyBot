import random
import logging
from datetime import datetime
from openai import AsyncOpenAI
from .config import Config

logger = logging.getLogger(__name__)


class PostGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
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
        - Длина: 2-4 предложения
        - Тон: дружелюбный, вдохновляющий
        - С эмодзи (Вдохновляющие)
        - C хештегами и обязательно в конце каждого поста
        - Тематика: мотивация в программировании, преодоление трудностей, рост как разработчика

        Создай уникальный пост, который поможет разработчикам начать день с позитивом.
        """

    def _get_fact_prompt(self):
        return """
        Ты - автор Telegram-канала "Таверна разработчика".
        Создай интересный IT-факт на русском языке.

        Требования:
        - Длина: 3-5 предложений
        - Тон: познавательный, увлекательный
        - С эмодзи (Вдохновляющие)
        - C хештегами и обязательно в конце каждого поста
        - Тематика: история IT, интересные факты о языках программирования, компаниях, технологиях

        Расскажи что-то действительно интересное, что может удивить даже опытных разработчиков.
        """

    def _get_meme_prompt(self):
        return """
        Ты - автор Telegram-канала "Таверна разработчика".
        Создай текстовый мем о программировании на русском языке.

        Требования:
        - Длина: 2-4 предложения
        - Тон: юмористический, ироничный
        - С эмодзи (Вдохновляющие)
        - C хештегами и обязательно в конце каждого поста
        - Тематика: типичные ситуации программистов, баги, дедлайны, код-ревью

        Создай что-то, над чем засмеются все разработчики, узнав себя.
        """

    def _get_devlog_prompt(self):
        return """
        Ты - автор Telegram-канала "Таверна разработчика".
        Создай devlog пост - заметку от лица разработчика на русском языке.

        Требования:
        - Длина: 4-6 предложений
        - Тон: личный, размышляющий
        - С эмодзи (Вдохновляющие)
        - C хештегами и обязательно в конце каждого поста
        - Тематика: размышления о коде, архитектуре, рефакторинге, новых технологиях

        Напиши как разработчик, который делится своими мыслями и опытом.
        """

    async def generate_post(self, post_type: str = None) -> str:
        """Генерирует пост заданного типа"""
        if post_type is None:
            post_type = random.choice(Config.POST_TYPES)

        if post_type not in self.prompts:
            raise ValueError(f"Неизвестный тип поста: {post_type}")

        try:
            logger.info(f"Генерация поста типа: {post_type}")

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

            logger.info(f"Пост успешно сгенерирован: {len(post_content)} символов")
            return post_content

        except Exception as e:
            logger.error(f"Ошибка при генерации поста: {e}")
            return self._get_fallback_post(post_type)

    def _get_fallback_post(self, post_type: str) -> str:
        """Резервные посты на случай ошибок с OpenAI"""
        fallback_posts = {
            'motivation': [
                "Каждый баг - это возможность стать лучше. Сегодня отличный день для написания чистого кода!",
                "Не бойтесь рефакторинга. Хороший код - это код, который легко менять.",
                "Лучшие разработчики не те, кто не делает ошибок, а те, кто умеет их быстро исправлять."
            ],
            'fact': [
                "Первый компьютерный баг был найден в 1947 году. Это была настоящая моль, застрявшая в реле компьютера Harvard Mark II.",
                "Термин 'debugging' появился благодаря адмиралу Грейс Хоппер, которая буквально извлекла насекомое из компьютера.",
                "Python назван в честь британского комедийного шоу 'Monty Python's Flying Circus', а не в честь змеи."
            ],
            'meme': [
                "Программист: 'Это работает на моей машине!' Пользователь: 'Тогда давайте поставим всем вашу машину.'",
                "99 маленьких багов в коде, 99 маленьких багов. Исправил один - появилось 117 новых багов в коде.",
                "Два состояния программиста: 'Я бог' и 'Я понятия не имею, что делаю'. Третьего не дано."
            ],
            'devlog': [
                "Сегодня потратил три часа на отладку. Оказалось, забыл добавить точку с запятой. Иногда простота обманчива.",
                "Рефакторинг старого кода - как археология. Каждый слой раскрывает новые тайны прошлых решений.",
                "Понял, что хорошая архитектура - это когда добавление новой функции не превращается в кошмар."
            ]
        }

        return random.choice(fallback_posts.get(post_type, fallback_posts['motivation']))

    def get_post_type_for_time(self, hour: int) -> str:
        """Определяет тип поста в зависимости от времени"""
        if hour == 8:
            return 'motivation'
        elif hour == 13:
            return random.choice(['fact', 'meme'])
        elif hour == 19:
            return random.choice(['devlog', 'fact'])
        else:
            return random.choice(Config.POST_TYPES)