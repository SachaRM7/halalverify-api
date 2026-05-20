from __future__ import annotations

from datetime import datetime, timezone

from models import db


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charity.id'), nullable=False)
    reviewer_name = db.Column(db.String(100), default='Anonymous')
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, default='')
    is_local_only = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'charity_id': self.charity_id,
            'reviewer_name': self.reviewer_name,
            'rating': self.rating,
            'review_text': self.review_text,
            'is_local_only': self.is_local_only,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
