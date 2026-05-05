from __future__ import annotations

from datetime import datetime, timezone

from models import db


class Charity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    website = db.Column(db.String(255), default='')
    registration_country = db.Column(db.String(100), default='')
    cause_areas = db.Column(db.String(255), default='')
    description = db.Column(db.Text, default='')
    reports_json = db.Column(db.JSON, default=list)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviews = db.relationship('Review', backref='charity', lazy=True, cascade='all, delete-orphan')
    donations = db.relationship('Donation', backref='charity', lazy=True)

    @classmethod
    def from_seed(cls, item: dict) -> 'Charity':
        return cls(
            name=item['name'],
            website=item.get('website', ''),
            registration_country=item.get('registration_country', ''),
            cause_areas=item.get('cause_areas', ''),
            description=item.get('description', ''),
            reports_json=item.get('reports_json', []),
        )

    @property
    def reports(self) -> list[str]:
        return self.reports_json or []

    @property
    def average_rating(self) -> float:
        if not self.reviews:
            return 0.0
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 2)

    @property
    def search_blob(self) -> str:
        return f'{self.name} {self.registration_country} {self.cause_areas} {self.description}'.lower()

    @classmethod
    def top_rated(cls, limit: int = 5, preferred_causes: str = '') -> list['Charity']:
        preferred = [item.strip().lower() for item in preferred_causes.split(',') if item.strip()]
        items = cls.query.all()
        if preferred:
            items = [item for item in items if any(cause in item.cause_areas.lower() for cause in preferred)] or items
        return sorted(items, key=lambda charity: (charity.average_rating, charity.name), reverse=True)[:limit]

    def to_dict(self, include_reviews: bool = True) -> dict:
        payload = {
            'id': self.id,
            'name': self.name,
            'website': self.website,
            'registration_country': self.registration_country,
            'cause_areas': self.cause_areas,
            'description': self.description,
            'reports': self.reports,
            'average_rating': self.average_rating,
            'num_reviews': len(self.reviews),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }
        if include_reviews:
            payload['reviews'] = [review.to_dict() for review in self.reviews]
        return payload
