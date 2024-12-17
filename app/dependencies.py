from functools import cache

from .config import Settings


@cache
def get_settings():
    return Settings()
