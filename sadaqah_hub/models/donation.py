from __future__ import annotations

from datetime import date

from models import db


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donation_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD', nullable=False)
    charity_name = db.Column(db.String(255), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charity.id'), nullable=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    category = db.Column(db.String(100), nullable=False)
    note = db.Column(db.Text, default='')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'donation_type': self.donation_type,
            'amount': self.amount,
            'currency': self.currency,
            'charity_name': self.charity_name,
            'charity_id': self.charity_id,
            'date': self.date.isoformat(),
            'category': self.category,
            'note': self.note,
        }
