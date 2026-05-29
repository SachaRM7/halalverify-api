from __future__ import annotations

from models import db


class GivingGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    annual_zakat_goal = db.Column(db.Float, default=0.0)
    monthly_sadaqah_target = db.Column(db.Float, default=0.0)
    assets = db.Column(db.Float, default=0.0)
    liabilities = db.Column(db.Float, default=0.0)
    nisab_threshold = db.Column(db.Float, default=5500.0)
    donor_name = db.Column(db.String(255), default='')
    telegram_chat_id = db.Column(db.String(255), default='')
    preferred_causes = db.Column(db.String(255), default='')

    @classmethod
    def get_primary(cls):
        return cls.query.order_by(cls.id.asc()).first()

    def to_dict(self) -> dict:
        return {
            'annual_zakat_goal': self.annual_zakat_goal,
            'monthly_sadaqah_target': self.monthly_sadaqah_target,
            'assets': self.assets,
            'liabilities': self.liabilities,
            'nisab_threshold': self.nisab_threshold,
            'donor_name': self.donor_name,
            'telegram_chat_id': self.telegram_chat_id,
            'preferred_causes': self.preferred_causes,
        }
