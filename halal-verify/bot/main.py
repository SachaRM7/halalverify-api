#!/usr/bin/env python3
from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CommandHandler, InlineQueryHandler, MessageHandler, filters

from api.config import get_settings
from bot.handlers.barcode import barcode_command, barcode_photo_handler
from bot.handlers.inline import inline_query_handler
from bot.handlers.report import report_command
from bot.handlers.verify import verify_command

settings = get_settings()


async def start_command(update: Update, context) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        'Assalamu alaikum. I can verify halal products and restaurants.\n\n'
        'Commands:\n'
        '/verify <name>\n'
        '/barcode\n'
        '/report <item_id> <reason>'
    )


async def stats_command(update: Update, context) -> None:
    if not update.message:
        return
    import httpx

    async with httpx.AsyncClient(base_url=settings.halalverify_api_url, timeout=settings.request_timeout_seconds) as client:
        response = await client.get('/v1/stats')
    if response.status_code != 200:
        await update.message.reply_text('Stats are unavailable right now.')
        return
    stats = response.json()
    await update.message.reply_text(
        f"Items: {stats['total_items']}\n"
        f"Sources: {stats['total_sources']}\n"
        f"Submissions: {stats['total_submissions']}\n"
        f"Reports: {stats['total_reports']}"
    )


def build_application() -> Application:
    token = settings.telegram_bot_token
    if not token:
        raise RuntimeError('TELEGRAM_BOT_TOKEN is required to run the bot.')

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('verify', verify_command))
    application.add_handler(CommandHandler('barcode', barcode_command))
    application.add_handler(CommandHandler('report', report_command))
    application.add_handler(CommandHandler('stats', stats_command))
    application.add_handler(InlineQueryHandler(inline_query_handler))
    application.add_handler(MessageHandler(filters.PHOTO, barcode_photo_handler))
    return application


def main() -> None:
    app = build_application()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
