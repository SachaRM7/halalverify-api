from __future__ import annotations

from datetime import datetime, timezone

import requests
from flask import current_app

from models import db
from models.charity import Charity


def sync_community_data(url: str) -> int:
    if not url:
        return 0
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        current_app.logger.warning('Community sync failed for %s', url)
        return 0

    imported = 0
    for item in payload.get('charities', []):
        existing = Charity.query.filter_by(name=item.get('name', '')).first()
        if existing:
            if not existing.website and item.get('website'):
                existing.website = item['website']
            if not existing.registration_country and item.get('registration_country'):
                existing.registration_country = item['registration_country']
            if not existing.cause_areas and item.get('cause_areas'):
                existing.cause_areas = item['cause_areas']
            if not existing.description and item.get('description'):
                existing.description = item['description']
            if not existing.reports_json and item.get('reports_json'):
                existing.reports_json = item['reports_json']
            existing.last_updated = datetime.now(timezone.utc)
        else:
            db.session.add(Charity.from_seed(item))
            imported += 1
    db.session.commit()
    return imported
