# image_generator.py | MIT License | 2025 | author: DimaLab
import logging
import asyncio
from openai import AsyncOpenAI
from .config import Config

logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def generate_image(self, prompt: str, style: str = "cozy") -> str:
        """Генерирует изображение и возвращает URL"""
        try:
            logger.info(f"Генерация изображения: {prompt[:50]}...")

            # Используем новую модель gpt-image-1
            response = await self.client.images.generate(
                model=Config.IMAGE_MODEL,
                prompt=prompt,
                size=Config.IMAGE_SIZE,
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            logger.info(f"Изображение успешно сгенерировано: {image_url}")
            return image_url

        except Exception as e:
            logger.error(f"Ошибка при генерации изображения: {e}")
            return None

    def get_morning_image_prompt(self) -> str:
        """Возвращает промпт для утреннего изображения в стиле Таверны разработчика"""
        return """
        Cozy developer workspace at sunrise, warm golden lighting through window, 
        laptop with code on screen, coffee cup, notebook, plant, programming books,
        peaceful morning atmosphere, wooden desk, soft shadows, 
        indie game art style, digital painting, warm color palette,
        developer's den, comfortable coding setup, morning productivity vibes
        """

    def get_fact_image_prompt(self) -> str:
        """Промпт для изображения к IT-факту"""
        return """
        Tech illustration, computer history, vintage computers mixed with modern technology,
        circuit boards, code snippets, tech timeline, digital art style,
        educational tech poster, programming concepts visualization,
        blue and green color scheme, clean professional design
        """

    def get_meme_image_prompt(self) -> str:
        """Промпт для мемного изображения"""
        return """
        Funny developer meme illustration, programmer at computer looking confused,
        multiple monitors with error messages, coffee cups everywhere,
        rubber duck on desk, comic book style, bright colors,
        humorous programming situation, developer life struggles
        """

    def get_devlog_image_prompt(self) -> str:
        """Промпт для devlog изображения"""
        return """
        Developer's evening reflection, dim lighting, multiple monitors,
        code architecture diagrams, notes scattered on desk,
        thoughtful atmosphere, deep work vibes, purple and blue tones,
        professional development environment, contemplative mood
        """