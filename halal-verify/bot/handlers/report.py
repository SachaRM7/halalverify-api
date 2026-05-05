from __future__ import annotations

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from api.config import get_settings

settings = get_settings()


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if len(context.args) < 2:
        await update.message.reply_text('Usage: /report <item_id> <reason>')
        return

    item_id = context.args[0]
    reason = ' '.join(context.args[1:])
    payload = {
        'item_id': item_id,
        'reporter_id': str(update.effective_user.id if update.effective_user else 'telegram-user'),
        'reason': reason,
    }

    async with httpx.AsyncClient(base_url=settings.halalverify_api_url, timeout=settings.request_timeout_seconds) as client:
        response = await client.post('/v1/reports', json=payload)

    if response.status_code != 201:
        await update.message.reply_text('Unable to create the report right now.')
        return

    report = response.json()
    await update.message.reply_text(f"Report created: {report['id']} (status: {report['status']})")
