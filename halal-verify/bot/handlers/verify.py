from __future__ import annotations

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from api.config import get_settings

settings = get_settings()


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text('Usage: /verify <product or restaurant name>')
        return

    query = ' '.join(context.args)
    async with httpx.AsyncClient(base_url=settings.halalverify_api_url, timeout=settings.request_timeout_seconds) as client:
        response = await client.get('/v1/search', params={'q': query, 'page_size': 5})

    if response.status_code != 200:
        await update.message.reply_text('The HalalVerify API is unavailable right now. Please try again later.')
        return

    payload = response.json()
    items = payload.get('items', [])
    if not items:
        await update.message.reply_text(f'No results found for: {query}')
        return

    lines = [f"Results for '{query}':"]
    for item in items:
        lines.append(f"- {item['name']} [{item['type']}] → {item['status']} ({item['confidence']})")
    await update.message.reply_text("\n".join(lines))
