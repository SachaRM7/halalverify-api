from __future__ import annotations

import asyncio
from datetime import date

from telegram import Bot

from app import create_app
from models.goal import GivingGoal
from services.zakat_calculator import calculate_zakat_due


def build_monthly_message(goal: GivingGoal | None, nisab_threshold: float) -> str:
    suggested = calculate_zakat_due(goal.assets, goal.liabilities, nisab_threshold) if goal else 0.0
    donor_name = goal.donor_name if goal and goal.donor_name else 'Donor'
    today = date.today().isoformat()
    return (
        f'Assalamu Alaikum {donor_name}.\\n'
        f'Date: {today}\\n'
        f'Nisab threshold: {nisab_threshold:.2f}\\n'
        f'Suggested zakat due: {suggested:.2f}\\n'
        'Open your Sadaqah dashboard to review giving progress.'
    )


async def send_monthly_reminder() -> bool:
    app = create_app()
    with app.app_context():
        goal = GivingGoal.get_primary()
        token = app.config.get('TELEGRAM_BOT_TOKEN', '')
        chat_id = (goal.telegram_chat_id if goal and goal.telegram_chat_id else app.config.get('TELEGRAM_CHAT_ID', ''))
        if not token or not chat_id:
            app.logger.warning('Telegram reminder skipped: token or chat_id missing')
            return False
        text = build_monthly_message(goal, goal.nisab_threshold if goal else app.config.get('DEFAULT_NISAB_THRESHOLD', 5500.0))
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=text)
        return True


def main() -> None:
    asyncio.run(send_monthly_reminder())


if __name__ == '__main__':
    main()
