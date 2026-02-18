"""
Exam AI Configuration
- Safe in dev/demo
- Strict in production (set ENV=prod)
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ENV: str = os.getenv("ENV", "dev").lower()  # dev | prod
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "0") == "1"  # if 1, never call OpenAI

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    DATA_DIR: str = os.getenv("DATA_DIR", "data/uploads")
    CACHE_DIR: str = os.getenv("CACHE_DIR", "data/cache")

    def validate(self):
        # Only hard-fail in prod
        if self.ENV == "prod" and not self.OPENAI_API_KEY and not self.DEMO_MODE:
            raise ValueError("OPENAI_API_KEY not found. Add it to .env or set DEMO_MODE=1")


settings = Settings()
settings.validate()
