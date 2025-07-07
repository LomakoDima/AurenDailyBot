# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1')
    IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'gpt-image-1')
    IMAGE_SIZE = os.getenv('IMAGE_SIZE', '1024x1024')
    IMAGE_QUALITY = os.getenv('IMAGE_QUALITY', 'high')
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Almaty')

    POST_SCHEDULE = [(8, 0), (15, 29), (20, 00)]

    POST_TYPES = [
        'motivation',
        'fact',
        'meme',
        'devlog'
    ]

    @classmethod
    def validate(cls):
        required_vars = ['BOT_TOKEN', 'CHANNEL_ID', 'OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]

        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")

        return True
