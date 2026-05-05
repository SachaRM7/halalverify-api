from __future__ import annotations

import httpx
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ContextTypes

from api.config import get_settings

settings = get_settings()


async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.inline_query:
        return

    query = update.inline_query.query.strip()
    if not query:
        return

    async with httpx.AsyncClient(base_url=settings.halalverify_api_url, timeout=settings.request_timeout_seconds) as client:
        response = await client.get('/v1/search', params={'q': query, 'page_size': 5})

    if response.status_code != 200:
        return

    results = []
    for item in response.json().get('items', []):
        results.append(
            InlineQueryResultArticle(
                id=item['item_id'],
                title=item['name'],
                description=f"{item['type']} → {item['status']} ({item['confidence']})",
                input_message_content=InputTextMessageContent(
                    f"{item['name']}\n"
                    f"Status: {item['status']}\n"
                    f"Type: {item['type']}\n"
                    f"Confidence: {item['confidence']}"
                ),
            )
        )
    await update.inline_query.answer(results, cache_time=30)
