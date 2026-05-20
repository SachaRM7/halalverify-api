from fastapi import Header

from api.config import get_settings

settings = get_settings()


async def get_api_key(x_api_key: str | None = Header(default=None)) -> str | None:
    if x_api_key and x_api_key in settings.parsed_api_keys:
        return x_api_key
    return None
