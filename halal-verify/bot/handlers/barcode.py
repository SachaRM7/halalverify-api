from __future__ import annotations

import tempfile

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from api.config import get_settings
from bot.services.barcode_lookup import extract_barcode_from_image_path, extract_barcode_from_text

settings = get_settings()


async def barcode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text('Send me a photo of a barcode. You can also include the digits in the caption to help recognition.')


async def barcode_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.photo:
        return

    photo = update.message.photo[-1]
    telegram_file = await photo.get_file()

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as handle:
        await telegram_file.download_to_drive(custom_path=handle.name)
        image_path = handle.name

    barcode = extract_barcode_from_text(update.message.caption) or extract_barcode_from_image_path(image_path)
    if not barcode:
        await update.message.reply_text('I could not read a barcode from that image. Please resend with the digits in the caption.')
        return

    async with httpx.AsyncClient(base_url=settings.halalverify_api_url, timeout=settings.request_timeout_seconds) as client:
        response = await client.get(f'/v1/verify/barcode/{barcode}')

    if response.status_code == 404:
        await update.message.reply_text(f'Barcode {barcode} is not in the database yet. Please submit it through the API or README workflow.')
        return
    if response.status_code != 200:
        await update.message.reply_text('Lookup failed. Please try again later.')
        return

    item = response.json()
    await update.message.reply_text(
        f"{item['name']} → {item['status']} ({item['confidence']})\n"
        f"Type: {item['type']}\n"
        f"Barcode: {item.get('barcode') or 'n/a'}"
    )
