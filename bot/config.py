import os

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN") or ""
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST") or "localhost"
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT") or 5672)
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER") or "root"
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD") or "root"