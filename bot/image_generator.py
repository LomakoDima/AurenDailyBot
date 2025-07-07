from __future__ import annotations
"""Image generation helper for AurenDailyBot – *fixed version*.

• Гарантирует корректный объект (URL **или** `BufferedInputFile`).
• Логирует полный ответ OpenAI для диагностики.
• Сохранил все вспомогательные «prompt‑factory» методы, чтобы ни один вызов
  из `PostGenerator` не упал.
"""

import asyncio
import base64
import logging
from typing import Optional, Union

from aiogram.types import BufferedInputFile
from openai import AsyncOpenAI

from .config import Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Main generation wrapper
# ---------------------------------------------------------------------------

class ImageGenerator:
    """Obtain an image from OpenAI in a Telegram‑friendly form.

    * Всегда просит `response_format='url'`.
    * Если всё же пришёл только `b64_json`, конвертирует в байты и
      возвращает `BufferedInputFile`.
    * Выход: `str` (URL) **или** `BufferedInputFile` – то, что готово для
      `Bot.send_photo()`.
    """

    def __init__(self) -> None:  # noqa: D401 – docstring выше
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    async def generate_image(
        self,
        prompt: str,
        *,
        style: str | None = None,
    ) -> Optional[Union[str, BufferedInputFile]]:
        """Generate and return an image for the given *prompt*.

        Если OpenAI не отвечает URL, но отдаёт `b64_json`, функция сама
        декодирует данные и возвращает «готовый» `BufferedInputFile`.
        Возвращает `None` при любой фатальной ошибке.
        """
        logger.info("Генерация изображения: %s", prompt[:80].replace("\n", " "))

        try:
            response = await self.client.images.generate(
                model=Config.IMAGE_MODEL,
                prompt=prompt,
                size=Config.IMAGE_SIZE,
                quality=Config.IMAGE_QUALITY,
                n=1,

            )

            logger.debug("RAW image response: %s", response)
            data = response.data[0]

            # 1. Предпочитаем URL.
            if url := getattr(data, "url", None):
                logger.info("Изображение получено (URL)")
                return url

            # 2. Fallback на base64.
            if b64 := getattr(data, "b64_json", None):
                try:
                    raw = base64.b64decode(b64)
                    logger.info("Изображение получено (base64→bytes)")
                    return BufferedInputFile(raw, filename="ai_image.png")
                except Exception as decode_err:  # pragma: no cover
                    logger.warning("Ошибка декодирования base64: %s", decode_err)

            logger.error("Ответ без URL и base64: %s", data)
            return None

        except Exception as exc:  # noqa: BLE001 – хотим видеть всё
            logger.error("Ошибка OpenAI Images API: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Prompt helpers – использует PostGenerator
    # ------------------------------------------------------------------

    @staticmethod
    def get_morning_image_prompt() -> str:
        """Prompt для утренней мотивации."""
        return (
            "Cozy developer workspace at sunrise, warm golden lighting through window, "
            "laptop with code on screen, coffee cup, notebook, plant, programming books, "
            "peaceful morning atmosphere, wooden desk, soft shadows, indie game art style, "
            "digital painting, warm color palette, developer's den, comfortable coding setup, morning productivity vibes"
        )

    @staticmethod
    def get_fact_image_prompt() -> str:
        """Prompt к IT‑факту."""
        return (
            "Tech illustration, computer history, vintage computers mixed with modern technology, "
            "circuit boards, code snippets, tech timeline, digital art style, educational tech poster, "
            "programming concepts visualization, blue and green color scheme, clean professional design"
        )

    @staticmethod
    def get_meme_image_prompt() -> str:
        """Prompt для мемов."""
        return (
            "Funny developer meme illustration, programmer at computer looking confused, "
            "multiple monitors with error messages, coffee cups everywhere, rubber duck on desk, "
            "comic book style, bright colors, humorous programming situation, developer life struggles"
        )

    @staticmethod
    def get_devlog_image_prompt() -> str:
        """Prompt для вечернего devlog."""
        return (
            "Developer's evening reflection, dim lighting, multiple monitors, code architecture diagrams, "
            "notes scattered on desk, thoughtful atmosphere, deep work vibes, purple and blue tones, "
            "professional development environment, contemplative mood"
        )


# ---------------------------------------------------------------------------
# Quick CLI smoke‑test (optional)
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover

    async def _smoke() -> None:
        gen = ImageGenerator()
        obj = await gen.generate_image("Hello world")
        print("Returned:", type(obj), "→", obj if isinstance(obj, str) else "<BufferedInputFile>")

    asyncio.run(_smoke())
