from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from models import db
from models.charity import Charity
from models.review import Review

api_bp = Blueprint('api', __name__, url_prefix='/api')


def _authorized() -> bool:
    expected = current_app.config.get('COMMUNITY_SHARED_PASSPHRASE', '')
    provided = request.headers.get('X-Community-Passphrase', '')
    return bool(expected) and provided == expected


@api_bp.get('/charities')
def list_charities():
    return jsonify([charity.to_dict(include_reviews=False) for charity in Charity.query.order_by(Charity.name.asc()).all()])


@api_bp.get('/charities/<int:charity_id>')
def charity_detail(charity_id: int):
    charity = db.get_or_404(Charity, charity_id)
    return jsonify(charity.to_dict(include_reviews=True))


@api_bp.get('/charities/<int:charity_id>/reports')
def charity_reports(charity_id: int):
    charity = db.get_or_404(Charity, charity_id)
    return jsonify({'charity_id': charity.id, 'reports': charity.reports})


@api_bp.post('/charities')
def create_charity():
    if not _authorized():
        return jsonify({'error': 'invalid passphrase'}), 403
    payload = request.get_json(force=True)
    charity = Charity(
        name=payload['name'],
        website=payload.get('website', ''),
        registration_country=payload.get('registration_country', ''),
        cause_areas=payload.get('cause_areas', ''),
        description=payload.get('description', ''),
        reports_json=payload.get('reports_json', []),
    )
    db.session.add(charity)
    db.session.commit()
    return jsonify(charity.to_dict(include_reviews=False)), 201


@api_bp.post('/charities/<int:charity_id>/reviews')
def create_review(charity_id: int):
    if not _authorized():
        return jsonify({'error': 'invalid passphrase'}), 403
    db.get_or_404(Charity, charity_id)
    payload = request.get_json(force=True)
    review = Review(
        charity_id=charity_id,
        reviewer_name=payload.get('reviewer_name', 'API User'),
        rating=int(payload['rating']),
        review_text=payload.get('review_text', ''),
        is_local_only=payload.get('is_local_only', False),
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201
